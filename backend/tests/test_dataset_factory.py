"""dataset_factory pipeline tests with the LLM and Blender stubbed out."""

import json

import dataset_factory


GOOD = {"character": "Aiko", "duration_seconds": 2, "reasoning": "wave to greet"}


def test_records_every_layer_and_counts_successes(monkeypatch):
    monkeypatch.setattr(
        dataset_factory,
        "generate_plan_with_critique",
        lambda c, p, s: {**GOOD, "_draft_plan": {"character": "Aiko"}, "_critique_received": "ok"},
    )
    monkeypatch.setattr(dataset_factory, "validate_script_headlessly", lambda script: (True, ""))

    result = dataset_factory.generate_dataset_batch("Aiko", ["wave"])
    assert result["total"] == 1 and result["successful"] == 1
    record = result["records"][0]
    assert record["draft_plan"] == {"character": "Aiko"}
    assert record["critique"] == "ok"
    assert "_draft_plan" not in record["polished_plan"]

    with open(result["filename"], encoding="utf-8") as f:
        assert json.loads(f.readline())["prompt"] == "wave"


def test_repair_loop_recovers_invalid_plan(monkeypatch):
    monkeypatch.setattr(
        dataset_factory, "generate_plan_with_critique", lambda c, p, s: {"character": "Aiko", "reasoning": "x"}
    )
    monkeypatch.setattr(dataset_factory, "repair_plan", lambda plan, err: dict(GOOD))
    monkeypatch.setattr(dataset_factory, "validate_script_headlessly", lambda script: (True, ""))

    record = dataset_factory.generate_dataset_batch("Aiko", ["wave"])["records"][0]
    assert record["validation_success"] is False
    assert "duration_seconds" in record["validation_error"]
    assert record["fixed_validation_success"] is True
    assert record["compiled_script"].startswith("import bpy")


def test_mock_plans_skip_repair(monkeypatch):
    monkeypatch.setattr(
        dataset_factory, "generate_plan_with_critique", lambda c, p, s: {**GOOD, "reasoning": "MOCK_REASONING"}
    )
    monkeypatch.setattr(dataset_factory, "validate_script_headlessly", lambda script: (False, "no blender"))

    def boom(*a):
        raise AssertionError("repair must not run for mock plans")

    monkeypatch.setattr(dataset_factory, "repair_plan", boom)
    record = dataset_factory.generate_dataset_batch("Aiko", ["wave"])["records"][0]
    assert record["fixed_plan"] is None
