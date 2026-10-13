# Blender LLM Animator & Fine-Tuning Studio

An agentic pipeline that turns a natural-language request ("Aiko nervously adjusts her collar before speaking") into a structured **Animation Intent Plan** with a local LLM, then compiles that plan deterministically into Blender Python (`bpy`). It also includes a RAG knowledge store for rig documentation and a synthetic-dataset factory for fine-tuning a small model (Qwen2.5-3B via Unsloth) on consumer GPUs (~6 GB VRAM).

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x%20CUDA-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Unsloth](https://img.shields.io/badge/Fine--Tuning-Unsloth-00C853?style=for-the-badge)](https://github.com/unslothai/unsloth)
[![Blender](https://img.shields.io/badge/3D%20Engine-Blender%204.x-E87D0D?style=for-the-badge&logo=blender&logoColor=white)](https://blender.org)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

> **Project status:** early stage. The plan → compile → script path works end to end. The semantic tools still emit *scaffold* keyframe code (armature/camera lookups, scene range, Rhubarb viseme keys); mapping intents to real rig controllers via RAG is on the [roadmap](03_ui_and_roadmap.md#11-phased-roadmap).

---

## Architecture: plan → compile → execute

The LLM never writes `bpy` code directly. It only reasons about *intent*; deterministic Python turns that intent into a script that can be validated and reproduced.

```
 User request + character
          │
          ▼
 ┌──────────────────────────┐   llm_planner.py  (Ollama; falls back to a mock plan)
 │ 1. LLM planner           │── draft → critique → polish (dataset mode)
 └────────────┬─────────────┘
              ▼  AnimationIntentPlan (JSON, validated by models.py)
 ┌──────────────────────────┐   rag.py  (ChromaDB knowledge store, rig notes)
 │ 2. Rig knowledge (RAG)   │   plan_compiler.get_rig_manifest_from_rag (stub today)
 └────────────┬─────────────┘
              ▼
 ┌──────────────────────────┐   plan_compiler.py + semantic_tools.py
 │ 3. Deterministic compiler│   rhubarb_bridge.py for lip-sync visemes
 └────────────┬─────────────┘
              ▼  bpy script
 ┌──────────────────────────┐   blender_validator.py (headless `blender -b -P`)
 │ 4. Blender               │   blender_bridge.py   (blender-mcp TCP socket)
 └──────────────────────────┘
```

| Module | Responsibility |
| :--- | :--- |
| `backend/main.py` | FastAPI app: plan, compile, knowledge, dataset and fine-tune status endpoints |
| `backend/config.py` | All settings, overridable via environment variables (see below) |
| `backend/models.py` | Pydantic schema for the Animation Intent Plan |
| `backend/llm_planner.py` | Prompts Ollama for plans; critique/polish and self-repair loops |
| `backend/plan_compiler.py` / `semantic_tools.py` | Plan → `bpy` script, with quoting-safe code generation |
| `backend/rag.py` | Lazy ChromaDB client (all-MiniLM-L6-v2 embeddings) |
| `backend/dataset_factory.py` | Generates validated JSONL training records |
| `backend/blender_validator.py` / `blender_bridge.py` | Headless validation / live execution in Blender |
| `backend/rhubarb_bridge.py` | Rhubarb Lip Sync CLI wrapper |
| `backend/finetune.py` | Local Unsloth QLoRA training + GGUF export |
| `frontend/` | React 19 + Vite UI (Fine-Tuning, Knowledge and Animation studios) |

Design rationale lives in [`00_overview.md`](00_overview.md), [`01_architecture.md`](01_architecture.md), [`02_planning_and_tools.md`](02_planning_and_tools.md) and [`03_ui_and_roadmap.md`](03_ui_and_roadmap.md).

---

## Local setup

**Requirements**

| Tool | Needed for | Notes |
| :--- | :--- | :--- |
| Python 3.10+ | Backend API | Required |
| Node.js 20.19+ / npm | Frontend | Required for the UI (Vite 8) |
| [Ollama](https://ollama.com) | Real plan generation | Optional: without it `/api/plan` returns a mock plan |
| Blender 4.x | Headless script validation, dataset generation | Optional |
| Rhubarb Lip Sync | Viseme extraction | Optional (`python scripts/download_rhubarb.py` on Windows) |
| NVIDIA GPU + CUDA | Local fine-tuning | Optional; or use the Colab/Kaggle notebooks |

### 1. Backend

```bash
# Option A: Makefile (Linux/macOS)
make install-dev        # creates backend/venv, installs API + test deps
make run-api            # http://localhost:8000  (docs at /docs)

# Option B: setup scripts
scripts/setup_env.sh --dev          # Linux/macOS
./scripts/setup_env.ps1             # Windows PowerShell

# Option C: manual
cd backend
python -m venv venv
source venv/bin/activate            # Windows: .\venv\Scripts\activate
pip install -r requirements.txt     # + requirements-dev.txt for tests
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm ci
cp .env.example .env.local          # optional: change VITE_API_URL
npm run dev                         # http://localhost:5173
```

### 3. Optional: Ollama model

```bash
ollama pull qwen3:4b                # default OLLAMA_MODEL
```

---

## Configuration

Settings are read from environment variables in `backend/config.py`; copy [`backend/.env.example`](backend/.env.example) for a full list. The most common ones:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `OLLAMA_URL` / `OLLAMA_MODEL` | `http://127.0.0.1:11434/api/generate` / `qwen3:4b` | Planner model endpoint |
| `BLENDER_EXECUTABLE` | `blender` on `PATH` | Headless validation binary |
| `BLEND_FILE` | unset | `.blend` scene to load during validation |
| `BLENDER_HOST` / `BLENDER_PORT` | `127.0.0.1` / `8123` | blender-mcp socket |
| `RHUBARB_EXECUTABLE` | `backend/tools/...` (Windows) or `rhubarb` on `PATH` | Lip-sync CLI |
| `CHROMA_DB_DIR` | `backend/chroma_db` | Vector store location |
| `DATASET_DIR` / `LORA_OUTPUT_DIR` | `backend/datasets` / `backend/lora_output` | Training data and adapters |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed browser origins |
| `LOG_LEVEL` | `INFO` | Backend log level |

The frontend reads `VITE_API_URL` (default `http://localhost:8000`).

---

## API reference

Interactive docs are served at `http://localhost:8000/docs` when the API is running.

| Method | Path | Body | Description |
| :--- | :--- | :--- | :--- |
| GET | `/` | – | Liveness message |
| GET | `/health` | – | Version and availability of Blender / Rhubarb |
| POST | `/api/plan` | `{character, request_text, scene_context?}` | Generate an Animation Intent Plan |
| POST | `/api/compile` | Animation Intent Plan JSON | Compile to a `bpy` script (422 if the plan is invalid) |
| POST | `/api/knowledge/add` | `{content, metadata?, doc_id?}` | Insert/replace a RAG document |
| POST | `/api/knowledge/query` | `{query, n_results? (1–50)}` | Semantic search over the knowledge store |
| POST | `/api/dataset/generate` | `{character, prompts[], scene_context?}` | Draft → critique → polish → validate → repair, saved as JSONL |
| GET | `/api/dataset/list` | – | Generated batches and record counts |
| GET | `/api/finetune/status` | – | Whether a LoRA adapter / GGUF export exists |
| GET | `/api/rigs/{character}` | – | Placeholder for the rig indexer |

Example:

```bash
curl -s -X POST localhost:8000/api/compile -H 'Content-Type: application/json' -d '{
  "character": "Aiko", "duration_seconds": 3,
  "emotion": {"primary": "nervous", "intensity": 0.6},
  "gestures": [{"type": "adjust_collar", "start": 1.0, "end": 1.6}]
}'
```

---

## Tests

```bash
make test               # or: cd backend && python -m pytest
```

The suite runs offline: Ollama and Rhubarb are disabled and datasets/Chroma are redirected to a temp directory.

---

## Fine-tuning workflow

Cloud notebooks (open the `.txt` file and import it as a notebook):

| Platform | Notebook File | Description | Action |
| :

1. **Generate data**: use the Fine-Tuning Studio (`/api/dataset/generate`, needs Ollama and ideally Blender) or `Dataset_Generator_Colab.txt`. Records land in `backend/datasets/*.jsonl`.
2. **Train**: upload the JSONL files to `Finetuning_Kaggle.txt` / `Finetuning_Colab.txt`, or locally run `pip install -r backend/requirements-finetune.txt && python backend/finetune.py` (Linux/WSL + CUDA). Training uses the self-repaired plan when the first attempt failed validation.
3. **Serve with Ollama**: create a `Modelfile` next to the exported GGUF, e.g.
   ```text
   FROM ./<exported-model>.Q4_K_M.gguf
   ```
   then `ollama create gwen-animator -f Modelfile` and set `OLLAMA_MODEL=gwen-animator`.

---

## Project structure

```text
.
├── backend/                 FastAPI app, compiler, RAG, dataset factory, fine-tuning
│   ├── tests/               pytest suite
│   ├── requirements*.txt    core / dev / finetune dependency groups
│   └── .env.example         documented configuration
├── frontend/                React + Vite UI
├── scripts/                 setup_env.sh, setup_env.ps1, download_rhubarb.py
├── docs/SETUP.md            detailed local-development guide
├── 0*_*.md, plan.md         design documents
├── *_Colab.txt, *_Kaggle.txt  notebooks
└── Makefile
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the development workflow.

---

## License

MIT, as declared by the author. (A `LICENSE` file has not been committed yet.)

## Acknowledgments

- [Unsloth](https://github.com/unslothai/unsloth) for fast 4-bit fine-tuning
- [Blender Foundation](https://www.blender.org/) for `bpy`
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) for viseme extraction
- [Hugging Face Transformers & TRL](https://github.com/huggingface/transformers) for training infrastructure
- [ChromaDB](https://www.trychroma.com/) for the vector store
