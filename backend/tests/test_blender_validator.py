"""blender_validator tests that stub out the Blender subprocess."""

import os
import subprocess
from types import SimpleNamespace

import blender_validator


def _capture_script_path(monkeypatch, result=None, exc=None):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["path"] = cmd[-1]
        assert os.path.exists(seen["path"])
        if exc:
            raise exc
        return result

    monkeypatch.setattr(blender_validator.subprocess, "run", fake_run)
    return seen


def test_success_removes_temp_script(monkeypatch):
    seen = _capture_script_path(monkeypatch, SimpleNamespace(returncode=0, stdout="", stderr=""))
    assert blender_validator.validate_script_headlessly("print('hi')") == (True, "")
    assert not os.path.exists(seen["path"])


def test_failure_returns_truncated_traceback(monkeypatch):
    noisy = "x" * 10_000 + "\nTraceback: NameError"
    seen = _capture_script_path(monkeypatch, SimpleNamespace(returncode=1, stdout="", stderr=noisy))
    ok, msg = blender_validator.validate_script_headlessly("boom")
    assert not ok
    assert msg.startswith("Blender exited with code 1.")
    assert msg.endswith("Traceback: NameError")
    assert len(msg) < 5000
    assert not os.path.exists(seen["path"])


def test_timeout_and_missing_binary_clean_up(monkeypatch):
    seen = _capture_script_path(monkeypatch, exc=subprocess.TimeoutExpired("blender", 1))
    ok, msg = blender_validator.validate_script_headlessly("pass")
    assert not ok and "timed out" in msg
    assert not os.path.exists(seen["path"])

    seen = _capture_script_path(monkeypatch, exc=FileNotFoundError())
    ok, msg = blender_validator.validate_script_headlessly("pass")
    assert not ok and "not found" in msg
    assert not os.path.exists(seen["path"])
