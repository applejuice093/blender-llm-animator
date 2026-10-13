"""Semantic action primitives that emit Blender Python (bpy) snippets.

Every value that comes from the LLM plan (character names, gesture types,
camera shots, file names) is untrusted text. Names are embedded with
``repr()`` so quotes cannot break the generated script, and free text that
ends up in comments is flattened to a single line so it cannot inject code.
"""

import rhubarb_bridge


def _comment(text) -> str:
    """Make ``text`` safe to place after a ``#`` on a single line."""
    return " ".join(str(text).split())


def generate_blender_imports() -> str:
    return "import bpy\nimport math\n\n"


def get_armature(character: str, manifest: dict) -> str:
    armature_name = manifest.get("armature", {}).get("name", "Rig")
    return f"armature = bpy.data.objects.get({armature_name!r})\n"


def set_scene_range(duration_seconds: float, manifest: dict) -> str:
    """Set the scene FPS and frame range so the clip length matches the plan."""
    fps = int(manifest.get("fps", 24))
    end_frame = max(1, int(round(duration_seconds * fps)))
    code = f"# Scene: {_comment(duration_seconds)}s at {fps} fps\n"
    code += "scene = bpy.context.scene\n"
    code += f"scene.render.fps = {fps}\n"
    code += "scene.frame_start = 0\n"
    code += f"scene.frame_end = {end_frame}\n\n"
    return code


def set_emotion(character: str, emotion: str, intensity: float, manifest: dict) -> str:
    code = f"# Set Emotion: {_comment(emotion)} (intensity {_comment(intensity)})\n"
    code += get_armature(character, manifest)
    code += "if armature:\n"
    code += "    pass # e.g. armature.pose.bones['CTRL_Smile'].rotation_euler = ...\n\n"
    return code


def gesture(character: str, g_type: str, start: float, end: float, intensity: float, manifest: dict) -> str:
    fps = manifest.get("fps", 24)
    start_frame = int(start * fps)
    end_frame = int(end * fps)

    code = (
        f"# Gesture: {_comment(g_type)} from {start}s (f{start_frame}) to {end}s (f{end_frame}) "
        f"with intensity {_comment(intensity)}\n"
    )
    code += get_armature(character, manifest)
    code += "if armature:\n"
    code += f"    pass # e.g. armature.pose.bones['CTRL_Arm'].keyframe_insert(data_path='rotation_euler', frame={start_frame})\n\n"
    return code


def lip_sync(character: str, audio_file: str, transcript: str, manifest: dict) -> str:
    code = f"# Lip Sync: mapping audio {_comment(audio_file)}\n"
    fps = manifest.get("fps", 24)
    mesh_name = manifest.get("mesh_name", f"{character}Mesh")

    if not audio_file:
        return code + "pass # No audio file provided\n\n"

    visemes = rhubarb_bridge.extract_visemes(audio_file, transcript)

    if not visemes:
        code += f"print({('Failed to extract visemes for ' + str(audio_file) + '.')!r})\n\n"
        return code

    code += f"mesh_obj = bpy.data.objects.get({mesh_name!r})\n"
    code += "if mesh_obj and mesh_obj.data.shape_keys:\n"

    for v in visemes:
        start_frame = int(v["start"] * fps)
        viseme_name = f"Viseme_{v['viseme']}"
        code += f"    # Viseme {_comment(v['viseme'])} at {v['start']}s\n"
        code += f"    if {viseme_name!r} in mesh_obj.data.shape_keys.key_blocks:\n"
        code += f"        kb = mesh_obj.data.shape_keys.key_blocks[{viseme_name!r}]\n"
        # Reset at previous frame to avoid blending issues, set to 1 at current frame
        code += "        kb.value = 0.0\n"
        code += f"        kb.keyframe_insert(data_path='value', frame=max(0, {start_frame}-1))\n"
        code += "        kb.value = 1.0\n"
        code += f"        kb.keyframe_insert(data_path='value', frame={start_frame})\n"

    code += "\n"
    return code


def camera_shot(shot_type: str) -> str:
    code = f"# Camera: {_comment(shot_type)}\n"
    code += "cam = bpy.data.objects.get('Camera')\n"
    code += "if cam:\n"
    code += f"    pass # position camera for {_comment(shot_type)}\n\n"
    return code
