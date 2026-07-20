# UI and Roadmap

## 10. The UI — Four Studios, One Shell

Single React/Vite frontend (dark, technical aesthetic), talking to one FastAPI backend over REST +
WebSocket for anything needing live progress.

**Fine-Tuning Studio**
- Browse Base Model, Browse/Build Dataset (upload `.jsonl` or launch the Dataset Factory)
- Config panel: simple mode (defaults) / advanced mode (rank, LR, seq length, batch, epochs)
- Start/Stop, live loss curve, VRAM usage meter, ETA
- Checkpoint manager + "chat with this checkpoint" test panel

**Knowledge Studio (RAG)**
- Upload reference docs; upload a `.blend` -> auto-runs the Rig Indexer -> shows both the manifest
  and the capability summary
- Embedding/indexing progress bar
- Collection browser + a "test a query" search box

**Blender Bridge**
- Connection status, live scene tree (from the Rig Indexer)
- Tool-call activity log — every Semantic Tool call and the code it generated, with accept/undo

**Animation Studio (Chat + Plan Editor)** — *the part that changed most*
- Main chat: describe any animation request in natural language
- Script/dialogue + audio upload (only relevant when `lip_sync` is involved)
- **Plan Preview & Edit panel (new):** shows the generated Animation Plan JSON as friendly sliders
  and fields (emotion intensity, gesture timing, camera shot) — you can nudge it before it's
  compiled, instead of only accepting or rejecting a black-box result
- "Generate Animation" runs Compile -> Execute -> Render as a visual progress stepper
- Before/after render preview

**Shared shell:** status bar (loaded model, VRAM usage), settings, Blender connection toggle.

---

## 11. Phased Roadmap

| Phase | Goal | Key Deliverables |
|---|---|---|
| **0 — Environment** | Everything installed and talking to each other | Blender + blender-mcp addon, Rhubarb CLI, Python env with Unsloth/LLaMA-Factory, base FastAPI + React shell |
| **1 — RAG-first MVP** | Prove the architecture before touching fine-tuning | Knowledge Studio functional; chat wired through an off-the-shelf instruct model (or cloud fallback) directly to blender-mcp — one real end-to-end success, even without the Plan/Tool layers yet |
| **2 — Semantic Tool Layer + Rig Indexer** | The deterministic core everything else depends on | Tool library from §5 built and unit-tested against a few real rigs; Rig Indexer producing manifests + capability summaries (§8); Rhubarb integration |
| **3 — Plan Compiler + Animation Studio v1** | Wire the Plan schema end to end | Planning done by an off-the-shelf instruct model (not yet fine-tuned) producing Plans per §6; Plan Compiler dispatching to the Tool Layer; Plan Preview/Edit UI |
| **4 — Dataset Factory** | Turn Phase 1–3 usage into training data | Distillation pipeline (§7), headless-Blender validation filter, curation UI |
| **5 — Fine-tuning pipeline** | Your own local planning brain | LLaMA Board (or your wrapped equivalent) driving Unsloth QLoRA on Qwen2.5-3B-Instruct; evaluate; attempt the 7B/8B stretch only after 3B works |
| **6 — Swap in the fine-tuned model** | Go fully offline for the default path | Fine-tuned model becomes the default planner; escape-hatch code-gen path wired for tool-layer gaps; cloud fallback kept optional |
| **7 — Polish** | The "final product" feel | Packaging (Tauri/Electron, optional), evaluation harness, continuous-improvement loop; optional graph-based rig representation and multi-stage specialist prompts if single-pass planning hits a quality ceiling |

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| 6GB VRAM too tight for 7B/8B fine-tuning | Default to 3B for training; larger models are inference-only unless you rent cloud GPU for occasional training runs |
| Semantic Tool Layer doesn't cover a requested action | Escape-hatch: fall back to raw code-gen (local Coder model or cloud) for that one request, and consider adding a permanent tool if the pattern recurs |
| Model plans a capability the rig doesn't have (e.g. walking with no leg rig) | Capability summary in context + dataset examples that explicitly teach "flag the limitation, don't fake it" |
| `execute_blender_code` is arbitrary code execution — a bad generation could corrupt a scene | Review/accept step in the Blender Bridge activity log; snapshot the `.blend` before each run |
| Small local model's creative/timing quality is weaker than cloud Claude via Antigravity | Hybrid mode: local for everyday iteration, optional cloud fallback for the hardest scenes |
| Blender MCP project is community-maintained with irregular update cadence | Pin a known-good addon/server version per project |

---

## 13. Assumptions I Made

- **"Graphs"** — Blender's Graph Editor F-curves for animated properties, plus an optional QA
  timeline chart in the UI. Flag it if you meant something else.
- **UI delivery** — a local web app (FastAPI + React) for iteration speed, optional Tauri/Electron
  wrap in Phase 7 for a double-click desktop app.
- **Language** — pipeline assumes English dialogue for lip sync (Rhubarb's strongest case);
  multilingual alternatives are noted in §4 if you need Hindi/other languages.
- **Single-pass planning over multi-stage specialists** — see the callout in §6 for the reasoning;
  flag it if you'd rather build the multi-stage version from the start.

---

## 14. Reference Links

- Blender MCP (bridge into Blender): https://github.com/ahujasid/blender-mcp
- Rhubarb Lip Sync (CLI): https://github.com/DanielSWolf/rhubarb-lip-sync
- Blender Rhubarb addon: https://github.com/scaredyfish/blender-rhubarb-lipsync
- Unsloth (fast/low-VRAM fine-tuning): https://unsloth.ai
- LLaMA-Factory + LLaMA Board (no-code fine-tuning UI): https://github.com/hiyouga/LLaMA-Factory
- ChromaDB (embedded vector store): https://www.trychroma.com
