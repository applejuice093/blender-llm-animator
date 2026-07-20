from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import rag_manager
import uuid
from models import AnimationIntentPlan
from plan_compiler import compile_plan
from blender_bridge import send_to_blender

app = FastAPI(title="Animation Pipeline Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnimationPlanRequest(BaseModel):
    character: str
    request_text: str
    scene_context: str = ""

class AddKnowledgeRequest(BaseModel):
    content: str
    metadata: dict = {}
    doc_id: str = None

class QueryKnowledgeRequest(BaseModel):
    query: str
    n_results: int = 3

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.post("/api/knowledge/add")
def add_knowledge(req: AddKnowledgeRequest):
    try:
        doc_id = req.doc_id if req.doc_id else str(uuid.uuid4())
        rag_manager.add_document(doc_id=doc_id, content=req.content, metadata=req.metadata)
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge/query")
def query_knowledge(req: QueryKnowledgeRequest):
    try:
        results = rag_manager.query(query_text=req.query, n_results=req.n_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from llm_planner import generate_plan
from dataset_factory import generate_dataset_batch, list_datasets

class DatasetRequest(BaseModel):
    character: str
    scene_context: str = ""
    prompts: list

@app.post("/api/dataset/generate")
def api_generate_dataset(req: DatasetRequest):
    try:
        result = generate_dataset_batch(req.character, req.prompts, req.scene_context)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dataset/list")
def api_list_datasets():
    try:
        return {"status": "success", "datasets": list_datasets()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os
import glob

@app.get("/api/finetune/status")
def get_finetune_status():
    status = {
        "lora_output_exists": os.path.exists("lora_output"),
        "gguf_exists": False,
        "gguf_file": None
    }
    if status["lora_output_exists"]:
        ggufs = glob.glob("lora_output/*.gguf")
        if ggufs:
            status["gguf_exists"] = True
            status["gguf_file"] = ggufs[0]
    return {"status": "success", "data": status}

@app.post("/api/plan")
def create_plan_endpoint(req: AnimationPlanRequest):
    try:
        plan_dict = generate_plan(req.character, req.request_text, req.scene_context)
        return {"status": "success", "plan": plan_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compile")
def compile_plan_endpoint(plan: dict):
    try:
        intent_plan = AnimationIntentPlan(**plan)
        script = compile_plan(intent_plan)
        return {
            "status": "success",
            "compiled_script": script
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rigs/{character}")
def get_rig_info(character: str):
    # Placeholder for RAG / Rig Indexer (Phase 1/2)
    return {"character": character, "status": "rag_not_implemented"}
