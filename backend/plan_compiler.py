"""Deterministic compiler: Animation Intent Plan (JSON) -> Blender Python script.

The LLM only decides *what* should happen; this module decides *how*, by
composing primitives from semantic_tools. Keeping this step deterministic is
what lets generated scripts be validated and reproduced.
"""

from typing import Union

from pydantic import ValidationError

import semantic_tools
from models import AnimationIntentPlan


class PlanCompilationError(ValueError):
    """Raised when a plan cannot be turned into a Blender script."""


def get_rig_manifest_from_rag(character: str) -> dict:
    """Return rig metadata for ``character``.

    TODO: look this up in the RAG store (rig indexer). For now a conventional
    ``<Character>Rig`` armature at 24 fps is assumed.
    """
    return {
        "character_name": character,
        "armature": {"name": f"{character}Rig"},
        "fps": 24,
    }


def compile_plan(plan: Union[AnimationIntentPlan, dict]) -> str:
    """Compile a validated plan (or a raw dict) into an executable bpy script.

    Raises:
        PlanCompilationError: if ``plan`` is a dict that fails schema validation
            or is of an unsupported type.
    """
    if isinstance(plan, dict):
        try:
            plan = AnimationIntentPlan(**plan)
        except ValidationError as exc:
            raise PlanCompilationError(f"Invalid animation plan: {exc}") from exc
    elif not isinstance(plan, AnimationIntentPlan):
        raise PlanCompilationError(
            f"compile_plan expected AnimationIntentPlan or dict, got {type(plan).__name__}"
        )

    manifest = get_rig_manifest_from_rag(plan.character)

    script = semantic_tools.generate_blender_imports()
    script += f"# Compiled Animation Plan for {semantic_tools._comment(plan.character)}\n\n"
    script += semantic_tools.set_scene_range(plan.duration_seconds, manifest)

    if plan.emotion:
        script += semantic_tools.set_emotion(
            plan.character,
            plan.emotion.primary,
            plan.emotion.intensity,
            manifest,
        )

    # Emit gestures in chronological order regardless of how the LLM listed them.
    for g in sorted(plan.gestures or [], key=lambda g: (g.start, g.end)):
        script += semantic_tools.gesture(
            plan.character,
            g.type,
            g.start,
            g.end,
            g.intensity,
            manifest,
        )

    if plan.lip_sync and plan.lip_sync.enabled:
        script += semantic_tools.lip_sync(
            plan.character,
            plan.lip_sync.audio_file,
            plan.lip_sync.transcript,
            manifest,
        )

    if plan.camera:
        script += semantic_tools.camera_shot(plan.camera.shot)

    return script
