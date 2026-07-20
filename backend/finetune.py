import os
import json
import glob
import torch

try:
    from unsloth import FastLanguageModel
    from trl import SFTTrainer
    from transformers import TrainingArguments
    from datasets import Dataset
except ImportError:
    print("Required training packages not found.")
    print("To run this script, please install Unsloth in a WSL environment:")
    print("pip install unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git")
    print("pip install --no-deps xformers trl peft accelerate bitsandbytes")

MAX_SEQ_LENGTH = 2048 # Fits in 6GB VRAM
MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct" 
DATASET_DIR = "datasets"
OUTPUT_DIR = "lora_output"

def load_data():
    records = []
    for filepath in glob.glob(os.path.join(DATASET_DIR, "*.jsonl")):
        with open(filepath, "r") as f:
            for line in f:
                record = json.loads(line)
                if record.get("validation_success", False):
                    instruction = f"Character: {record['character']}\nRequest: {record['prompt']}\nGenerate the JSON animation plan."
                    response = json.dumps(record['plan'])
                    records.append({
                        "instruction": instruction,
                        "output": response
                    })
    if len(records) > 0:
        return Dataset.from_list(records)
    return None

def format_prompt(examples):
    system_prompt = "You are an expert animation director. You must output a valid JSON object representing an animation intent plan, and NOTHING ELSE."
    texts = []
    for instruction, output in zip(examples["instruction"], examples["output"]):
        text = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
        texts.append(text)
    return {"text": texts}

def main():
    print(f"Loading datasets from {DATASET_DIR}...")
    dataset = load_data()
    if dataset is None or len(dataset) == 0:
        print("No valid datasets found. Generate some in the Fine-Tuning Studio first.")
        return

    print(f"Found {len(dataset)} training examples.")
    dataset = dataset.map(format_prompt, batched=True)

    print("Loading base model in 4-bit...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = MODEL_NAME,
        max_seq_length = MAX_SEQ_LENGTH,
        dtype = None,
        load_in_4bit = True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # LoRA rank
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = MAX_SEQ_LENGTH,
        dataset_num_proc = 2,
        packing = False,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 60, # For quick demonstration. Increase for real training.
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
        ),
    )

    print("Starting training...")
    trainer_stats = trainer.train()

    print(f"Saving LoRA adapters to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("Exporting to GGUF for Ollama (Q4_K_M)...")
    try:
        model.save_pretrained_gguf(OUTPUT_DIR, tokenizer, quantization_method = "q4_k_m")
        print(f"Success! You can now import the model in {OUTPUT_DIR} into Ollama.")
    except Exception as e:
        print(f"GGUF Export failed: {e}. You may need to manually merge using llama.cpp.")

if __name__ == "__main__":
    main()
