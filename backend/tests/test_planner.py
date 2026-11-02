"""Unit tests for llm_planner helpers that do not need a running Ollama."""

from llm_planner import parse_json_object


def test_parse_plain_object():
    assert parse_json_object('{"character": "Aiko"}') == {"character": "Aiko"}


def test_parse_strips_markdown_fence():
    text = '```json\n{"character": "Aiko", "duration_seconds": 2}\n```'
    assert parse_json_object(text) == {"character": "Aiko", "duration_seconds": 2}


def test_parse_extracts_object_from_chatter():
    text = 'Sure! Here is the plan: {"character": "Aiko"} Hope that helps.'
    assert parse_json_object(text) == {"character": "Aiko"}


def test_parse_rejects_non_object_json():
    # Valid JSON, but callers rely on dict methods such as .get().
    assert parse_json_object("[1, 2, 3]") == {}
    assert parse_json_object('"just a string"') == {}


def test_parse_handles_empty_and_garbage():
    assert parse_json_object("") == {}
    assert parse_json_object(None) == {}
    assert parse_json_object("not json at all") == {}
