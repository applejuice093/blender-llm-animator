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
