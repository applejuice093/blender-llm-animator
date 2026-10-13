# Contributing

Thanks for helping improve the Blender LLM Animator. This project is small, so the process is light.

## Workflow

1. Create a branch from `main` (`feature/...`, `fix/...`, `docs/...`).
2. Set up the environment with `make install-dev install-frontend` (see [docs/SETUP.md](docs/SETUP.md)).
3. Make focused commits with clear messages, for example `fix(compiler): ...` or `docs: ...`.
4. Before opening a pull request, run:
   ```bash
   make test              # backend pytest suite
   make build-frontend    # tsc + vite build
   make lint-frontend     # oxlint
   ```
5. Open a PR against `main` describing what changed and why.

## Guidelines

- **Keep the compiler deterministic.** The LLM produces plans; `plan_compiler.py` and `semantic_tools.py` must stay plain, testable Python. Embed any value from a plan in generated code with `repr()` (or `_comment()` for comments), never with raw string interpolation.
- **Schema changes** in `models.py` should be reflected in `SYSTEM_PROMPT` (`llm_planner.py`) and covered by a test in `backend/tests/test_models.py`.
- **Configuration** belongs in `config.py` as an environment variable with a sensible default; document it in `backend/.env.example` and the README table.
- **Optional tools** (Ollama, Blender, Rhubarb, GPUs) must stay optional. The API and the test suite have to run without them.
- **Notebooks** (`*_Colab.txt`, `*_Kaggle.txt`) are JSON `.ipynb` files saved as `.txt`. Edit them in Jupyter/Colab and keep the record format compatible with `dataset_factory.py`.
- Don't commit datasets, model weights, `chroma_db/`, `.env` files or virtualenvs (already in `.gitignore`).
