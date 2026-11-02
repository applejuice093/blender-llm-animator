"""FastAPI backend for the Blender LLM Animator.

Pipeline: natural-language request -> LLM plan (/api/plan) -> deterministic
bpy script (/api/compile) -> Blender. Also exposes the RAG knowledge store and
the synthetic dataset factory used for fine-tuning.

Run locally:  uvicorn main:app --reload --port 8000   (from backend/)
"""

import glob
import logging
import os
import shutil
import uuid
from typing import List, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator

from config import BLENDER_EXECUTABLE, CORS_ORIGINS, LOG_LEVEL, LORA_OUTPUT_DIR, RHUBARB_EXECUTABLE
from dataset_factory import generate_dataset_batch, list_datasets
from llm_planner import generate_plan
from models import AnimationIntentPlan
from plan_compiler import PlanCompilationError, compile_plan
from rag import rag_manager

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("animator.api")

API_VERSION = "0.2.0"

app = FastAPI(
    title="Animation Pipeline Backend",
    version=API_VERSION,
    description="Plan -> Compile -> Blender animation pipeline with RAG and dataset generation.",
)

# Browsers only need CORS for the Vite dev server; override with CORS_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Request models ----------------------------------------------------------

def _not_blank(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("must not be blank")
    return value.strip()


class AnimationPlanRequest(BaseModel):
    character: str = Field(min_length=1, max_length=100)
    request_text: str = Field(min_length=1, max_length=4000)
    scene_context: str = Field(default="", max_length=4000)

    _strip = field_validator("character", "request_text")(_not_blank)


class AddKnowledgeRequest(BaseModel):
    content: str = Field(min_length=1, max_length=100_000)
    metadata: dict = Field(default_factory=dict)
    doc_id: Optional[str] = Field(default=None, max_length=200)

    _strip = field_validator("content")(_not_blank)

    @field_validator("metadata")
    @classmethod
    def _flat_metadata(cls, metadata: dict) -> dict:
        # ChromaDB only stores flat str/int/float/bool values; anything else
        # used to surface as an opaque 500 from inside Chroma.
        for key, value in metadata.items():
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError(
                    f"metadata[{key!r}] must be a string, number or boolean, got {type(value).__name__}"
                )
        return metadata


class QueryKnowledgeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    n_results: int = Field(default=3, ge=1, le=50)

    _strip = field_validator("query")(_not_blank)


class DatasetRequest(BaseModel):
    character: str = Field(min_length=1, max_length=100)
    scene_context: str = Field(default="", max_length=4000)
    prompts: List[str] = Field(min_length=1, max_length=200)

    _strip = field_validator("character")(_not_blank)

    @field_validator("prompts")
    @classmethod
    def _drop_blank_prompts(cls, prompts: List[str]) -> List[str]:
        cleaned = [p.strip() for p in prompts if p and p.strip()]
        if not cleaned:
            raise ValueError("at least one non-empty prompt is required")
        too_long = [i for i, p in enumerate(cleaned) if len(p) > 4000]
        if too_long:
            raise ValueError(f"prompts must be at most 4000 characters (index {too_long[0]})")
        return cleaned


# --- Health ------------------------------------------------------------------

@app.get("/")
def read_root():
    """Liveness probe kept for backwards compatibility with the frontend."""
    return {"status": "Backend is running"}


@app.get("/health")
def health():
    """Cheap health check reporting which optional local tools are available."""
    return {
        "status": "ok",
        "version": API_VERSION,
        "tools": {
            "blender": bool(shutil.which(BLENDER_EXECUTABLE) or os.path.exists(BLENDER_EXECUTABLE)),
            "rhubarb": bool(RHUBARB_EXECUTABLE and os.path.exists(RHUBARB_EXECUTABLE)),
        },
    }


# --- Knowledge (RAG) ---------------------------------------------------------

@app.post("/api/knowledge/add")
def add_knowledge(req: AddKnowledgeRequest):
    """Insert or replace a document in the ChromaDB knowledge store."""
    doc_id = req.doc_id or str(uuid.uuid4())
    try:
        rag_manager.add_document(doc_id=doc_id, content=req.content, metadata=req.metadata)
    except Exception:
        logger.exception("Failed to add knowledge document %s", doc_id)
        raise HTTPException(status_code=500, detail="Could not store the document; see server log.")
    return {"status": "success", "doc_id": doc_id}


@app.post("/api/knowledge/query")
def query_knowledge(req: QueryKnowledgeRequest):
    """Semantic search over the knowledge store; returns raw Chroma results."""
    try:
        return rag_manager.query(query_text=req.query, n_results=req.n_results)
    except Exception:
        logger.exception("Knowledge query failed")
        raise HTTPException(status_code=500, detail="Knowledge query failed; see server log.")


# --- Dataset factory ---------------------------------------------------------

@app.post("/api/dataset/generate")
def api_generate_dataset(req: DatasetRequest):
    """Run draft -> critique -> polish -> validate -> repair for each prompt."""
    logger.info("Generating dataset batch: character=%s prompts=%d", req.character, len(req.prompts))
    try:
        result = generate_dataset_batch(req.character, req.prompts, req.scene_context)
    except Exception:
        logger.exception("Dataset generation failed")
        raise HTTPException(status_code=500, detail="Dataset generation failed; see server log.")
    return {"status": "success", "data": result}


@app.get("/api/dataset/list")
def api_list_datasets():
    """List generated ``*.jsonl`` batches with record counts."""
    try:
        return {"status": "success", "datasets": list_datasets()}
    except Exception:
        logger.exception("Listing datasets failed")
        raise HTTPException(status_code=500, detail="Could not list datasets; see server log.")


@app.get("/api/finetune/status")
def get_finetune_status():
    """Report whether a LoRA adapter / GGUF export exists in LORA_OUTPUT_DIR."""
    status = {
        "lora_output_exists": os.path.isdir(LORA_OUTPUT_DIR),
        "gguf_exists": False,
        "gguf_file": None,
    }
    if status["lora_output_exists"]:
        ggufs = sorted(glob.glob(os.path.join(LORA_OUTPUT_DIR, "*.gguf")))
        if ggufs:
            status["gguf_exists"] = True
            status["gguf_file"] = os.path.relpath(ggufs[0], os.path.dirname(LORA_OUTPUT_DIR))
    return {"status": "success", "data": status}


# --- Plan / compile ----------------------------------------------------------

@app.post("/api/plan")
def create_plan_endpoint(req: AnimationPlanRequest):
    """Ask the LLM for an Animation Intent Plan (falls back to a mock plan)."""
    try:
        plan_dict = generate_plan(req.character, req.request_text, req.scene_context)
    except Exception:
        logger.exception("Plan generation failed")
        raise HTTPException(status_code=500, detail="Plan generation failed; see server log.")
    # Tell the UI up front whether /api/compile will accept this plan, instead
    # of letting the user discover a schema problem one click later.
    try:
        AnimationIntentPlan(**plan_dict)
        valid, validation_error = True, None
    except ValidationError as e:
        valid, validation_error = False, str(e)
    return {
        "status": "success",
        "plan": plan_dict,
        "valid": valid,
        "validation_error": validation_error,
        "mock": plan_dict.get("reasoning") == "MOCK_REASONING",
    }


@app.post("/api/compile")
def compile_plan_endpoint(plan: dict = Body(..., description="Animation Intent Plan JSON")):
    """Compile an Animation Intent Plan into a Blender Python script.

    Returns 422 with the validation message if the plan does not match the schema.
    """
    try:
        script = compile_plan(plan)
    except PlanCompilationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Unexpected compile failure")
        raise HTTPException(status_code=500, detail="Compilation failed; see server log.")
    return {"status": "success", "compiled_script": script}


@app.get("/api/rigs/{character}")
def get_rig_info(character: str):
    """Placeholder for the RAG rig indexer (Phase 1/2 of the roadmap)."""
    return {"character": character, "status": "rag_not_implemented"}
