from models import AnimationIntentPlan
import semantic_tools

def get_rig_manifest_from_rag(character: str) -> dict:
    # Mocking rig manifest lookup
    return {
        "character_name": character,
        "armature": {"name": f"{character}Rig"},
        "fps": 24,
    }

def compile_plan(plan: AnimationIntentPlan) -> str:
    manifest = get_rig_manifest_from_rag(plan.character)
    
    script = semantic_tools.generate_blender_imports()
    script += f"# Compiled Animation Plan for {plan.character}\n\n"
    
    if plan.emotion:
        script += semantic_tools.set_emotion(
            plan.character, 
            plan.emotion.primary, 
            plan.emotion.intensity, 
            manifest
        )
        
    if plan.gestures:
        for g in plan.gestures:
            script += semantic_tools.gesture(
                plan.character, 
                g.type, 
                g.start, 
                g.end, 
                g.intensity, 
                manifest
            )
            
    if plan.lip_sync and plan.lip_sync.enabled:
        script += semantic_tools.lip_sync(
            plan.character, 
            plan.lip_sync.audio_file, 
            plan.lip_sync.transcript, 
            manifest
        )
        
    if plan.camera:
        script += semantic_tools.camera_shot(plan.camera.shot)
        
    return script
