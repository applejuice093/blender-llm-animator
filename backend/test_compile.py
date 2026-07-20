from models import AnimationIntentPlan
from plan_compiler import compile_plan

mock_plan = {
  "character": "Aiko",
  "duration_seconds": 5.2,
  "emotion": { "primary": "nervous", "intensity": 0.6 },
  "eye_behavior": { "target": "camera", "blink_rate": "increased", "eye_darts": True },
  "lip_sync": { "enabled": True, "audio_file": "line_04.wav", "transcript": "Hello everyone..." },
  "gestures": [
    { "start": 2.3, "end": 3.1, "type": "raise_right_hand", "intensity": 0.4 },
    { "start": 4.0, "end": 4.6, "type": "adjust_collar", "intensity": 1.0 }
  ],
  "camera": { "shot": "medium_close_up", "movement": "static" }
}

intent_plan = AnimationIntentPlan(**mock_plan)
compiled_script = compile_plan(intent_plan)
print("--- COMPILED BLENDER SCRIPT ---")
print(compiled_script)
print("-------------------------------")
