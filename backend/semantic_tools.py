def generate_blender_imports():
    return "import bpy\nimport math\n\n"

def get_armature(character: str, manifest: dict):
    armature_name = manifest.get("armature", {}).get("name", "Rig")
    return f"armature = bpy.data.objects.get('{armature_name}')\n"

def set_emotion(character: str, emotion: str, intensity: float, manifest: dict) -> str:
    code = f"# Set Emotion: {emotion} (intensity {intensity})\n"
    code += get_armature(character, manifest)
    code += f"if armature:\n"
    code += f"    pass # e.g. armature.pose.bones['CTRL_Smile'].rotation_euler = ...\n\n"
    return code

def gesture(character: str, g_type: str, start: float, end: float, intensity: float, manifest: dict) -> str:
    fps = manifest.get("fps", 24)
    start_frame = int(start * fps)
    end_frame = int(end * fps)
    
    code = f"# Gesture: {g_type} from {start}s (f{start_frame}) to {end}s (f{end_frame}) with intensity {intensity}\n"
    code += get_armature(character, manifest)
    code += f"if armature:\n"
    code += f"    pass # e.g. armature.pose.bones['CTRL_Arm'].keyframe_insert(data_path='rotation_euler', frame={start_frame})\n\n"
    return code

import rhubarb_bridge

def lip_sync(character: str, audio_file: str, transcript: str, manifest: dict) -> str:
    code = f"# Lip Sync: mapping audio {audio_file}\n"
    fps = manifest.get("fps", 24)
    mesh_name = manifest.get("mesh_name", f"{character}Mesh")
    
    if not audio_file:
        return code + "pass # No audio file provided\n\n"
        
    visemes = rhubarb_bridge.extract_visemes(audio_file, transcript)
    
    if not visemes:
        code += f"print('Failed to extract visemes for {audio_file}.')\n\n"
        return code
        
    code += f"mesh_obj = bpy.data.objects.get('{mesh_name}')\n"
    code += f"if mesh_obj and mesh_obj.data.shape_keys:\n"
    
    for v in visemes:
        start_frame = int(v["start"] * fps)
        viseme_name = f"Viseme_{v['viseme']}"
        code += f"    # Viseme {v['viseme']} at {v['start']}s\n"
        code += f"    if '{viseme_name}' in mesh_obj.data.shape_keys.key_blocks:\n"
        code += f"        kb = mesh_obj.data.shape_keys.key_blocks['{viseme_name}']\n"
        # Reset at previous frame to avoid blending issues, set to 1 at current frame
        code += f"        kb.value = 0.0\n"
        code += f"        kb.keyframe_insert(data_path='value', frame=max(0, {start_frame}-1))\n"
        code += f"        kb.value = 1.0\n"
        code += f"        kb.keyframe_insert(data_path='value', frame={start_frame})\n"
        
    code += "\n"
    return code

def camera_shot(shot_type: str) -> str:
    code = f"# Camera: {shot_type}\n"
    code += f"cam = bpy.data.objects.get('Camera')\n"
    code += f"if cam:\n"
    code += f"    pass # position camera for {shot_type}\n\n"
    return code
