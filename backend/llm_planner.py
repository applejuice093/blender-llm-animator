import json
import urllib.request
import re
from models import AnimationIntentPlan

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:4b"

SYSTEM_PROMPT = """You are an expert animation director. You must output a valid JSON object representing an animation intent plan, and NOTHING ELSE. No markdown, no explanations, just raw JSON.
The JSON must conform to this schema:
{
  "reasoning": "string - think step by step about the character's motivation, the scene context, and the physical constraints before outputting the rest of the plan. Do NOT mention other drafts, critiques, or director feedback.",
  "character": "string",
  "duration_seconds": 5.0,
  "emotion": {
    "primary": "string",
    "secondary": "string or null",
    "intensity": 0.5
  },
  "body_language": {
    "posture": "string",
    "weight_shift": "string or null",
    "energy": "string or float",
    "tension": "string or float or null"
  },
  "head_motion": {
    "type": "string",
    "frequency": "string or float or null",
    "amplitude": "string or float or null"
  },
  "eye_behavior": {
    "target": "string",
    "eye_darts": false,
    "blink_rate": "string or float",
    "avoid_eye_contact": false
  },
  "facial_expression": {
    "brows": "string",
    "mouth": "string",
    "jaw": "string"
  },
  "breathing": {
    "rate": "string or float",
    "depth": "string or float or null"
  },
  "lip_sync": {
    "enabled": false,
    "audio_file": null,
    "transcript": null
  },
  "gestures": [
    {
      "type": "string",
      "target": "string or null",
      "start": 0.0,
      "end": 1.0,
      "intensity": 1.0
    }
  ],
  "timeline": [
    {
      "time": 0.0,
      "action": "string"
    }
  ],
  "locomotion": null,
  "camera": {
    "shot": "string",
    "movement": "string"
  },
  "notes": "string"
}
"""

def call_ollama(prompt: str, system: str) -> dict:
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "format": "json"
    }
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # Check response first
            resp_text = result.get("response", "").strip()
            if not resp_text:
                # Fall back to thinking field (for reasoning models)
                resp_text = result.get("thinking", "").strip()
                
            if not resp_text:
                print("Ollama returned empty response and thinking fields.")
                return {}
                
            # Clean up markdown block wraps if present
            clean_text = resp_text
            if clean_text.startswith("```"):
                # strip markdown blocks
                lines = clean_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
                
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError as jde:
                # Try to extract the first valid JSON object using regex
                match = re.search(r'\{.*\}', clean_text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except:
                        pass
                print(f"Failed to parse JSON: {clean_text[:200]}... Error: {jde}")
                return {}
    except Exception as e:
        print(f"Ollama failed ({e})")
        return {}

def generate_plan(character: str, request_text: str, scene_context: str = "") -> dict:
    prompt = f"Scene Context: {scene_context}\nCharacter: {character}\nRequest: {request_text}\nGenerate the JSON animation plan."
    plan_dict = call_ollama(prompt, SYSTEM_PROMPT)
    if not plan_dict:
        return get_mock_plan(character, request_text, scene_context)
    return plan_dict

def generate_plan_with_critique(character: str, request_text: str, scene_context: str = "") -> dict:
    """
    3-step generation: Draft -> Critique -> Polish
    """
    # 1. Draft
    draft_plan = generate_plan(character, request_text, scene_context)
    if not draft_plan or draft_plan.get("reasoning") == "MOCK_REASONING":
        return draft_plan # Fallback hit
        
    # 2. Critique
    critique_system = "You are a Senior Animation Director evaluating an animation plan JSON. Output a JSON object with a single key 'critique' containing your notes on what needs to be improved based on the original request and scene context."
    critique_prompt = f"Scene Context: {scene_context}\nOriginal Request: {request_text}\nDraft Plan:\n{json.dumps(draft_plan)}\nEvaluate this plan."
    critique_res = call_ollama(critique_prompt, critique_system)
    critique_text = critique_res.get("critique", "No critique provided.")
    
    # 3. Polish
    polish_prompt = (
        f"Scene Context: {scene_context}\n"
        f"Original Request: {request_text}\n"
        f"Draft Plan:\n{json.dumps(draft_plan)}\n"
        f"Critique from Director:\n{critique_text}\n\n"
        "Generate the final, improved JSON animation plan incorporating the critique. "
        "CRITICAL INSTRUCTION: Write the 'reasoning' field in your response as if you are planning this animation from scratch. "
        "Do NOT mention 'critique', 'draft', 'corrections', or 'director'. Your reasoning must be written entirely as a "
        "clean animator's thought process (e.g. 'To show nervousness, the character will...')."
    )
    final_plan = call_ollama(polish_prompt, SYSTEM_PROMPT)
    
    if not final_plan:
        return draft_plan
        
    # We save critique and draft inside the final dict so dataset_factory can record it
    final_plan["_draft_plan"] = draft_plan
    final_plan["_critique_received"] = critique_text
    return final_plan

def repair_plan(failed_plan: dict, error_message: str) -> dict:
    """
    Self-Repair Loop: Take a failed plan and repair it using the validation error.
    """
    repair_prompt = (
        f"The following animation plan JSON failed validation.\n"
        f"Failed Plan:\n{json.dumps(failed_plan)}\n\n"
        f"Validation Error:\n{error_message}\n\n"
        "Please fix the plan and output a fully valid JSON matching the schema. "
        "Ensure all missing fields are added or corrected according to the validation error."
    )
    repaired_plan = call_ollama(repair_prompt, SYSTEM_PROMPT)
    return repaired_plan

def get_mock_plan(character: str, request_text: str, scene_context: str = "") -> dict:
    return {
        "reasoning": "MOCK_REASONING",
        "character": character,
        "duration_seconds": 5.0,
        "emotion": {
            "primary": "neutral",
            "secondary": None,
            "intensity": 0.5
        },
        "body_language": {
            "posture": "relaxed",
            "weight_shift": None,
            "energy": "medium",
            "tension": None
        },
        "head_motion": {
            "type": "subtle_nod",
            "frequency": "occasional",
            "amplitude": "small"
        },
        "eye_behavior": {
            "target": "camera",
            "blink_rate": "normal",
            "eye_darts": False,
            "avoid_eye_contact": False
        },
        "facial_expression": {
            "brows": "neutral",
            "mouth": "closed",
            "jaw": "relaxed"
        },
        "breathing": {
            "rate": "normal",
            "depth": "normal"
        },
        "lip_sync": {
            "enabled": False,
            "audio_file": None,
            "transcript": None
        },
        "gestures": [],
        "timeline": [],
        "locomotion": None,
        "camera": {
            "shot": "medium_shot",
            "movement": "static"
        },
        "notes": f"Generated based on request: '{request_text}'"
    }
