"""Synthetic dataset generation: draft -> critique -> polish -> validate -> repair.

Each prompt produces one JSONL record in ``DATASET_DIR`` containing every layer
of the pipeline, which finetune.py and the Colab/Kaggle notebooks consume.
"""

import json
import logging
import os
import uuid

from config import DATASET_DIR
from llm_planner import generate_plan_with_critique
from models import AnimationIntentPlan
from plan_compiler import compile_plan

logger = logging.getLogger(__name__)


def generate_dataset_batch(character: str, prompts: list, scene_context: str = "") -> dict:
    """Run the full generation pipeline for each prompt and append to a new batch file."""
    os.makedirs(DATASET_DIR, exist_ok=True)
    batch_id = str(uuid.uuid4())[:8]
    filename = os.path.join(DATASET_DIR, f"batch_{batch_id}.jsonl")
    
    results = []
    for prompt in prompts:
        # 1. Generate Plan with Critique
        plan_dict = generate_plan_with_critique(character, prompt, scene_context)
        
        draft_plan = plan_dict.pop("_draft_plan", None)
        critique = plan_dict.pop("_critique_received", None)
        polished_plan = plan_dict
        
        # 2. Validate Polished Plan
        validation_success = False
        validation_error = ""
        script = ""
        fixed_plan = None
        fixed_validation_success = None
        fixed_validation_error = None
        
        try:
            intent_plan = AnimationIntentPlan(**polished_plan)
            script = compile_plan(intent_plan)
            compile_success = True
        except Exception as e:
            compile_success = False
            validation_error = f"Pydantic Validation Error: {str(e)}"
            
        from blender_validator import validate_script_headlessly
        
        if compile_success:
            validation_success, validation_error = validate_script_headlessly(script)
            
        # 3. Self-Repair Loop if validation failed (and it's not a fallback mock plan)
        if not validation_success and polished_plan.get("reasoning") != "MOCK_REASONING":
            logger.info("Validation failed for prompt %r. Initiating self-repair...", prompt)
            from llm_planner import repair_plan
            
            fixed_plan = repair_plan(polished_plan, validation_error)
            
            try:
                fixed_intent = AnimationIntentPlan(**fixed_plan)
                fixed_script = compile_plan(fixed_intent)
                fixed_compile_success = True
            except Exception as e:
                fixed_compile_success = False
                fixed_validation_error = f"Pydantic Validation Error in Repair: {str(e)}"
                
            if fixed_compile_success:
                fixed_validation_success, fixed_validation_error = validate_script_headlessly(fixed_script)
                if fixed_validation_success:
                    script = fixed_script # update with the working script
            else:
                fixed_validation_success = False
        
        # 4. Save record with all pipeline layers
        record = {
            "scene_context": scene_context,
            "prompt": prompt,
            "character": character,
            "draft_plan": draft_plan,
            "critique": critique,
            "polished_plan": polished_plan,
            "validation_success": validation_success,
            "validation_error": validation_error,
            "fixed_plan": fixed_plan,
            "fixed_validation_success": fixed_validation_success,
            "fixed_validation_error": fixed_validation_error,
            "compiled_script": script
        }
        results.append(record)
        
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")
            
    return {
        "batch_id": batch_id,
        "filename": filename,
        "total": len(results),
        "successful": sum(1 for r in results if r["validation_success"] or r.get("fixed_validation_success")),
        "records": results
    }

def list_datasets():
    """List ``*.jsonl`` batch files with their record counts (empty if none yet)."""
    if not os.path.isdir(DATASET_DIR):
        return []
    datasets = []
    for f in sorted(os.listdir(DATASET_DIR)):
        if f.endswith(".jsonl"):
            filepath = os.path.join(DATASET_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                count = sum(1 for line in file if line.strip())
            datasets.append({
                "filename": f,
                "record_count": count
            })
    return datasets
