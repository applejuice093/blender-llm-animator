import ast

import pytest

from plan_compiler import PlanCompilationError, compile_plan


def test_accepts_raw_dict(sample_plan):
    script = compile_plan(sample_plan)
    ast.parse(script)


def test_invalid_dict_raises_plan_compilation_error():
    with pytest.raises(PlanCompilationError, match="Invalid animation plan"):
        compile_plan({"character": "Aiko"})


def test_wrong_type_raises():
    with pytest.raises(PlanCompilationError):
        compile_plan("not a plan")


def test_scene_range_matches_duration(sample_plan):
    script = compile_plan(sample_plan)
    # 5.2s * 24fps = 124.8 -> 125
    assert "scene.render.fps = 24" in script
    assert "scene.frame_end = 125" in script


def test_gestures_emitted_in_chronological_order(sample_plan):
    script = compile_plan(sample_plan)
    assert script.index("raise_right_hand") < script.index("adjust_collar")
    assert "(f55)" in script  # 2.3s * 24


def test_disabled_lip_sync_and_no_camera_are_skipped():
    script = compile_plan({
        "character": "Aiko",
        "duration_seconds": 1,
        "lip_sync": {"enabled": False},
    })
    assert "Lip Sync" not in script
    assert "Camera" not in script


def test_lip_sync_without_rhubarb_still_compiles(sample_plan):
    script = compile_plan(sample_plan)
    ast.parse(script)
    assert "Failed to extract visemes for line_04.wav." in script


def test_quote_in_character_name_produces_valid_python():
    script = compile_plan({
        "character": "O'Neil",
        "duration_seconds": 2,
        "emotion": {"primary": "happy", "intensity": 0.5},
        "gestures": [{"type": "wave", "start": 0, "end": 1}],
    })
    ast.parse(script)
    assert "bpy.data.objects.get(\"O'NeilRig\")" in script


def test_newlines_in_llm_strings_cannot_inject_code():
    script = compile_plan({
        "character": "Aiko",
        "duration_seconds": 2,
        "gestures": [{"type": "wave\nimport os; os.system('boom')", "start": 0, "end": 1}],
        "camera": {"shot": "wide\nevil()", "movement": "static"},
    })
    tree = ast.parse(script)
    calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert "system" not in calls
    assert not any(line.startswith("evil(") for line in script.splitlines())
