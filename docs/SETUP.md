# Local development setup

This guide expands the README quickstart with platform notes and troubleshooting.

## 1. Clone and create the backend environment

```bash
git clone https://github.com/applejuice093/blender-llm-animator.git
cd blender-llm-animator
```

| Platform | Command |
| :--- | :--- |
| Linux / macOS | `scripts/setup_env.sh --dev` or `make install-dev` |
| Windows (PowerShell) | `./scripts/setup_env.ps1` then `backend\venv\Scripts\pip install -r backend\requirements-dev.txt` |
| WSL2 (for local fine-tuning) | `scripts/setup_env.sh --dev --finetune` (install a CUDA build of torch first) |

All of these create `backend/venv/`, which is git-ignored.

Dependency groups:

- `backend/requirements.txt`: FastAPI, Uvicorn, Pydantic v2, ChromaDB (enough to run the API)
- `backend/requirements-dev.txt`: adds pytest and httpx
- `backend/requirements-finetune.txt`: adds torch, unsloth, trl, transformers, datasets, peft, accelerate, bitsandbytes for `finetune.py`

## 2. Configure (optional)

```bash
cp backend/.env.example backend/.env
# edit values, then load them into your shell before starting the API:
set -a && source backend/.env && set +a
```

Relative paths (`CHROMA_DB_DIR`, `DATASET_DIR`, `LORA_OUTPUT_DIR`, `TOOLS_DIR`) are resolved against `backend/`, so the API behaves the same no matter which directory you launch it from.

## 3. Run

```bash
make run-api          # terminal 1: http://localhost:8000 (Swagger UI at /docs)
make run-frontend     # terminal 2: http://localhost:5173
curl localhost:8000/health
```

`/health` reports `tools.blender` and `tools.rhubarb`, so you can check whether the optional binaries were found.

## 4. Optional components

### Ollama (plan generation)

Install Ollama, then `ollama pull qwen3:4b` (or set `OLLAMA_MODEL`). If Ollama is not reachable, `/api/plan` returns a deterministic mock plan with `"reasoning": "MOCK_REASONING"` and dataset generation skips the repair loop for it.

### Blender (validation and dataset generation)

Blender is only used for headless validation (`blender -b -P script.py`). Put `blender` on your `PATH` or set `BLENDER_EXECUTABLE`, for example:

- Linux: `/usr/bin/blender` or `~/blender-4.2/blender`
- macOS: `/Applications/Blender.app/Contents/MacOS/Blender`
- Windows: `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`

Set `BLEND_FILE` to load a rigged scene before running the script.

### Rhubarb Lip Sync

- Windows: `python scripts/download_rhubarb.py` downloads it to `backend/tools/`, the default location.
- Linux/macOS: download the release for your OS from the [Rhubarb releases page](https://github.com/DanielSWolf/rhubarb-lip-sync/releases) and either put `rhubarb` on `PATH` or set `RHUBARB_EXECUTABLE`.

Without Rhubarb, lip-sync sections still compile but print a "Failed to extract visemes" message inside the generated script.

## 5. Tests

```bash
make test
```

`backend/tests/conftest.py` redirects datasets and Chroma to a temp directory and disables Ollama/Rhubarb, so tests never touch your real data and need no network.

## Troubleshooting

| Symptom | Fix |
| :--- | :--- |
| Browser shows CORS errors | Add the UI origin to `CORS_ORIGINS` (comma-separated) and restart the API |
| `Blender executable not found` in validation errors | Install Blender or set `BLENDER_EXECUTABLE` |
| First knowledge query is slow | ChromaDB downloads the all-MiniLM-L6-v2 ONNX model (~80 MB) on first use |
| `/api/compile` returns 422 | The plan does not match the schema; the `detail` field names the failing field |
| `finetune.py` prints "Required training packages not found" | `pip install -r backend/requirements-finetune.txt` in a CUDA-capable Linux/WSL env |
