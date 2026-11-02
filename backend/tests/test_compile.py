"""End-to-end compile of the reference plan (formerly a print-only script)."""

import ast

from models import AnimationIntentPlan
from plan_compiler import compile_plan


def test_reference_plan_compiles_to_valid_python(sample_plan):
    script = compile_plan(AnimationIntentPlan(**sample_plan))
    ast.parse(script)  # must be syntactically valid Python
    assert script.startswith("import bpy")
    assert "# Compiled Animation Plan for Aiko" in script
    assert "bpy.data.objects.get('AikoRig')" in script
    assert "# Camera: medium_close_up" in script


def test_gesture_frames_round_instead_of_truncating():
    # 4.1 s * 30 fps is 122.99999999999999 in floating point; it must be frame 123.
    import semantic_tools

    code = semantic_tools.gesture("Aiko", "wave", 4.1, 8.2, 1.0, {"fps": 30, "armature": {"name": "AikoRig"}})
    assert "(f123)" in code and "(f246)" in code


def test_scene_range_uses_same_rounding():
    import semantic_tools

    code = semantic_tools.set_scene_range(4.1, {"fps": 30})
    assert "scene.frame_end = 123" in code
