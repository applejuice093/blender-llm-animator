import pytest
from pydantic import ValidationError

from llm_planner import get_mock_plan
from models import AnimationIntentPlan, GesturePlan


def test_minimal_plan_defaults():
    plan = AnimationIntentPlan(character="Aiko", duration_seconds=1.0)
    assert plan.gestures == []
    assert plan.timeline == []
    assert plan.emotion is None


def test_list_defaults_are_not_shared():
    a = AnimationIntentPlan(character="A", duration_seconds=1)
    b = AnimationIntentPlan(character="B", duration_seconds=1)
    a.gestures.append(GesturePlan(type="wave", start=0, end=1))
    assert b.gestures == []


def test_null_lists_from_llm_become_empty():
    plan = AnimationIntentPlan(character="Aiko", duration_seconds=1, gestures=None, timeline=None)
    assert plan.gestures == [] and plan.timeline == []


def test_character_is_stripped():
    assert AnimationIntentPlan(character="  Aiko ", duration_seconds=1).character == "Aiko"


@pytest.mark.parametrize("character", ["", "   "])
def test_blank_character_rejected(character):
    with pytest.raises(ValidationError):
        AnimationIntentPlan(character=character, duration_seconds=1)


@pytest.mark.parametrize("duration", [0, -2.5])
def test_non_positive_duration_rejected(duration):
    with pytest.raises(ValidationError):
        AnimationIntentPlan(character="Aiko", duration_seconds=duration)


def test_missing_required_fields_rejected():
    with pytest.raises(ValidationError) as exc:
        AnimationIntentPlan(character="Aiko")
    assert "duration_seconds" in str(exc.value)


def test_gesture_end_before_start_rejected():
    with pytest.raises(ValidationError, match="ends before it starts"):
        GesturePlan(type="wave", start=2.0, end=1.0)


def test_negative_gesture_time_rejected():
    with pytest.raises(ValidationError):
        GesturePlan(type="wave", start=-1.0, end=1.0)


def test_numeric_or_descriptive_values_accepted():
    plan = AnimationIntentPlan(
        character="Aiko",
        duration_seconds=3,
        emotion={"primary": "happy", "intensity": "high"},
        breathing={"rate": 0.8},
    )
    assert plan.emotion.intensity == "high"
    assert plan.breathing.rate == 0.8


def test_mock_plan_matches_schema():
    plan = AnimationIntentPlan(**get_mock_plan("Aiko", "wave hello"))
    assert plan.reasoning == "MOCK_REASONING"
    assert plan.character == "Aiko"
