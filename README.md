# 🎭 Blender LLM Animator & Fine-Tuning Studio

> An end-to-end agentic AI pipeline for fine-tuning open-weights LLMs (Qwen2.5-3B via Unsloth) to generate structured 3D character animation plans and executable Blender Python (`bpy`) keyframing scripts — completely locally on consumer hardware (6GB VRAM friendly).

---

## 🌟 Key Highlights

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x%20CUDA-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Unsloth](https://img.shields.io/badge/Fine--Tuning-Unsloth-00C853?style=for-the-badge)](https://github.com/unslothai/unsloth)
[![Blender](https://img.shields.io/badge/3D%20Engine-Blender%204.x-E87D0D?style=for-the-badge&logo=blender&logoColor=white)](https://blender.org)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

---

## ⚡ Quick Links & Cloud Notebooks

Fine-tune models on cloud GPUs (T4 / A100) and export quantised `.gguf` files directly for local inference:

| Platform | Notebook File | Description | Action |
| :--- | :--- | :--- | :--- |
| **Kaggle** | [`Finetuning_Kaggle.txt`](Finetuning_Kaggle.txt) | Unsloth 4-bit fine-tuning (Qwen2.5-3B) on Kaggle T4 GPUs + GGUF export | [![Kaggle](https://img.shields.io/badge/Open_in-Kaggle-20BEFF?style=flat-square&logo=kaggle&logoColor=white)](https://kaggle.com) |
| **Google Colab** | [`Finetuning_Colab.txt`](Finetuning_Colab.txt) | Colab GPU fine-tuning workflow with GGUF export for Ollama | [![Colab](https://img.shields.io/badge/Open_in-Colab-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com) |
| **Google Colab** | [`Dataset_Generator_Colab.txt`](Dataset_Generator_Colab.txt) | Synthetic dataset generator with self-repair critic feedback loops | [![Colab](https://img.shields.io/badge/Generate-Dataset-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com) |

---

## 🏛️ System Architecture: *Plan → Compile → Execute*

To prevent LLM hallucination in raw Python code generation, this system separates animation intent reasoning from low-level execution into three decoupled layers:

```
                                    +-----------------------------------------+
                                    |         User Prompt & Character         |
                                    | "Gwen trembles with anxious energy..."  |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |      1. Fine-Tuned Model (Unsloth)      |
                                    |   Generates Structured Animation Plan   |
                                    |   (Emotions, Body Language, Gestures)   |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |       2. Rig RAG Knowledge Base         |
                                    |     (ChromaDB + Rig Controllers)        |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |      3. Plan Compiler & Semantic Tools  |
                                    |    Deterministic Python Script Builder  |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |         Blender Execution (bpy)         |
                                    |      Keyframing & Rhubarb Lip-Sync      |
                                    +-----------------------------------------+
```

1. **Fine-Tuned LLM (`Qwen2.5-3B-Instruct`)**: Outputs a clean, rig-agnostic JSON **Animation Intent Plan** (emotion intensity, body language, facial expression, head motion, gesture timing, and camera shots).
2. **RAG Vector Store (ChromaDB)**: Supplies character-specific rig rules, controller names, bone rotation limits, and viseme mapping sheets without requiring model retraining.
3. **Plan Compiler & Semantic Tool Layer**: Deterministically translates the JSON plan into validated, executable Blender Python (`bpy`) keyframe scripts.

---

## ✨ Features

- 🎬 **Natural Language to 3D Keyframes**: Turn prompts like *"Gwen beams with ecstatic joy, bouncing on her toes"* into formatted animation keyframes.
- ⚙️ **Optimized for 6GB VRAM**: fine-tuning uses **Unsloth 4-bit QLoRA** (QLoRA r=16, max_seq_length=2048), taking ~4.5GB VRAM during training and under 4GB during inference.
- 🔁 **Self-Repair Dataset Synthesizer**: Built-in dataset pipeline with a critic model that validates generated JSON plans against rig constraints and fixes broken parameters automatically.
- 🗣️ **Rhubarb Lip-Sync Integration**: Automatic viseme extraction from audio files mapped directly to Blender character speech shapes.
- 🖥️ **Integrated FineTuningStudio UI**: A modern React + Tailwind web UI featuring:
  - **Fine-Tuning Studio**: Dataset prep & Unsloth training launcher.
  - **Knowledge Studio**: Rig guide & RAG document manager.
  - **Blender Bridge**: Live script preview, execution, and validator logs.
  - **Animation Studio**: Natural language chat & plan inspector.

---

## 🛠️ Project Structure

```text
Finetuning/
├── backend/
│   ├── main.py                  # FastAPI Backend Orchestrator
│   ├── llm_planner.py           # LLM Animation Director & Plan Generator
│   ├── plan_compiler.py         # Plan Compiler -> Blender Python (bpy)
│   ├── semantic_tools.py        # Semantic Action Primitives (wave, nod, gesture)
│   ├── blender_validator.py     # Headless Blender Syntax & Rig Validator
│   ├── dataset_factory.py       # Self-Repair Dataset Generator & Critic
│   ├── finetune.py              # Unsloth Training Wrapper
│   ├── rag.py                   # ChromaDB Vector RAG Engine
│   └── rhubarb_bridge.py        # Rhubarb Lip Sync Integration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── FineTuningStudio.tsx  # React FineTuning & Animation Studio
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── scripts/
│   ├── download_rhubarb.py      # Rhubarb CLI auto-downloader
│   └── setup_env.ps1            # Environment setup script
├── Finetuning_Kaggle.txt        # Kaggle GPU Training Notebook Script
├── Finetuning_Colab.txt         # Google Colab Training Notebook Script
└── Dataset_Generator_Colab.txt  # Dataset Generation Notebook Script
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites

- **Python**: 3.10 or 3.11
- **Node.js**: 18+ and `npm`
- **Blender**: 4.x installed on your PATH or custom directory
- **GPU**: NVIDIA GPU with CUDA support (4GB+ VRAM required, 6GB recommended)

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

---

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Start the Vite development server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🎯 Fine-Tuning Workflow (Kaggle / Colab)

1. **Generate Synthetic Training Dataset**:
   - Run `Dataset_Generator_Colab.txt` on Colab to generate validated `.jsonl` animation records.
2. **Train LoRA Adapter & Export GGUF**:
   - Open `Finetuning_Kaggle.txt` on Kaggle (T4 GPU).
   - Upload your `.jsonl` files.
   - Run the notebook to train `Qwen2.5-3B-Instruct` with Unsloth.
   - Download the exported `q4_k_m.gguf` file from `/kaggle/working/lora_output/`.
3. **Deploy to Ollama**:
   ```bash
   ollama create gwen-animator -f Modelfile
   ```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 🙌 Acknowledgments

- [Unsloth AI](https://github.com/unslothai/unsloth) for ultra-fast 4-bit fine-tuning.
- [Blender Foundation](https://www.blender.org/) for the Python `bpy` 3D engine.
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) for automated viseme extraction.
- [Hugging Face Transformers & TRL](https://github.com/huggingface/transformers) for training infrastructure.
