"""finetune.select_training_plan must match the Colab/Kaggle notebook logic."""

from finetune import select_training_plan


def test_prefers_repaired_plan_when_repair_succeeded():
    rec = {"validation_success": False, "polished_plan": {"v": "p"},
           "fixed_validation_success": True, "fixed_plan": {"v": "f"}}
    assert select_training_plan(rec) == {"v": "f"}


def test_uses_polished_plan_when_it_validated():
    rec = {"validation_success": True, "polished_plan": {"v": "p"},
           "fixed_validation_success": None, "fixed_plan": None}
    assert select_training_plan(rec) == {"v": "p"}


def test_skips_records_that_never_validated():
    rec = {"validation_success": False, "polished_plan": {"v": "p"},
           "fixed_validation_success": False, "fixed_plan": {"v": "f"}}
    assert select_training_plan(rec) is None


def test_legacy_record_without_plan_keys_is_skipped():
    assert select_training_plan({"validation_success": True}) is None
