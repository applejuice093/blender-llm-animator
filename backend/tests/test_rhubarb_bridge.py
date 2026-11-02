"""rhubarb_bridge tests with the CLI stubbed out."""

import json
import subprocess
from types import SimpleNamespace

import rhubarb_bridge


def _enable(monkeypatch, tmp_path):
    exe = tmp_path / "rhubarb"
    exe.write_text("")
    audio = tmp_path / "line.wav"
    audio.write_bytes(b"RIFF")
    monkeypatch.setattr(rhubarb_bridge, "RHUBARB_EXECUTABLE", str(exe))
    return str(audio)


def test_missing_executable_returns_empty(monkeypatch):
    monkeypatch.setattr(rhubarb_bridge, "RHUBARB_EXECUTABLE", "")
    assert rhubarb_bridge.extract_visemes("line.wav") == []


def test_parses_mouth_cues(monkeypatch, tmp_path):
    audio = _enable(monkeypatch, tmp_path)
    out = {"mouthCues": [{"start": 0.0, "end": 0.2, "value": "A"}, {"start": 0.2, "end": 0.5, "value": "X"}]}
    seen = {}

    def fake_run(cmd, **kwargs):
        seen.update(kwargs)
        return SimpleNamespace(stdout=json.dumps(out))

    monkeypatch.setattr(rhubarb_bridge.subprocess, "run", fake_run)
    assert rhubarb_bridge.extract_visemes(audio) == [
        {"start": 0.0, "end": 0.2, "viseme": "A"},
        {"start": 0.2, "end": 0.5, "viseme": "X"},
    ]
    assert seen["timeout"] == rhubarb_bridge.RHUBARB_TIMEOUT


def test_timeout_returns_empty(monkeypatch, tmp_path):
    audio = _enable(monkeypatch, tmp_path)

    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))

    monkeypatch.setattr(rhubarb_bridge.subprocess, "run", fake_run)
    assert rhubarb_bridge.extract_visemes(audio, "hello") == []
