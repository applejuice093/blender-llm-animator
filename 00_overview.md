# Local LLM + RAG + Blender MCP Animation Pipeline — Project Plan

> Goal: a fully local system where you drop in a rigged character (+ rig guide) and describe *any*
> animation — talking, gesturing, walking, reacting, camera work — and a fine-tuned local model
> (backed by RAG, driving Blender through MCP) produces it, with **zero code touched by you at
> runtime**. Everything (fine-tuning, RAG, Blender bridge, chat) lives behind one UI.

**Target hardware:** RTX 3050 6GB VRAM · 16GB RAM · i5 12th-gen. Every recommendation below is
chosen to actually run on this box. You're already running ComfyUI/LTX Video and a custom
LoRA-selector node on this same card for the companion-app project, so the VRAM discipline here
isn't new territory — same budget, different workload.

**v2 changelog:** merged in the "animation director" architecture from the second conversation you
pasted — structured intent plans, a semantic tool layer, dataset split by what's transferable vs.
character-specific — and broadened scope from "speaking animation" to animation in general. I kept
the good ideas from that conversation but re-sized a few of them (model choice, multi-stage
planning, graph RAG) to actually fit a single 6GB card run by one person, rather than an
enterprise-scale build. Details on what changed and why are inline.

---

## Table of Contents
1. [The Core Design Decision: Plan, Then Compile, Then Execute](01_architecture.md#1-the-core-design-decision-plan-then-compile-then-execute)
2. [Hardware Reality Check](01_architecture.md#2-hardware-reality-check)
3. [System Architecture](01_architecture.md#3-system-architecture)
4. [Model & Tooling Choices](01_architecture.md#4-model--tooling-choices)
5. [The Semantic Tool Layer](02_planning_and_tools.md#5-the-semantic-tool-layer)
6. [The Animation Intent Plan](02_planning_and_tools.md#6-the-animation-intent-plan)
7. [The Fine-Tuning Dataset](02_planning_and_tools.md#7-the-fine-tuning-dataset)
8. [Understanding "Production Quality" Rigs](02_planning_and_tools.md#8-understanding-production-quality-rigs)
9. [Pipeline Walkthrough — Two Examples](02_planning_and_tools.md#9-pipeline-walkthrough--two-examples)
10. [The UI — Four Studios, One Shell](03_ui_and_roadmap.md#10-the-ui--four-studios-one-shell)
11. [Phased Roadmap](03_ui_and_roadmap.md#11-phased-roadmap)
12. [Risks & Mitigations](03_ui_and_roadmap.md#12-risks--mitigations)
13. [Assumptions I Made](03_ui_and_roadmap.md#13-assumptions-i-made)
14. [Reference Links](03_ui_and_roadmap.md#14-reference-links)

---
