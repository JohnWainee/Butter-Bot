from pathlib import Path

from butter_bot.style import brief_from_violations, fix_paths, fix_text, lint_paths


def test_fix_replaces_latin_and_exclamation():
    result = fix_text("Use containers, e.g. Docker!")
    assert "for example," in result.text
    assert "!" not in result.text
    assert result.changed


def test_fix_leaves_code_blocks_alone():
    text = "Prose with e.g. an issue.\n\n```\ncode with e.g. kept!\n```\n"
    result = fix_text(text)
    assert "code with e.g. kept!" in result.text
    assert "for example," in result.text


def test_fix_reports_remaining_judgment_items():
    result = fix_text("The doc is written by the bot.")
    assert any(v.rule_id == "passive-voice" for v in result.remaining)
    brief = brief_from_violations(result.remaining)
    assert brief and brief[0].instruction


def test_paths_roundtrip(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Use tools, e.g. Docker.\n", encoding="utf-8")
    assert lint_paths([tmp_path])
    results = fix_paths([tmp_path], write=True)
    assert results[0].changed
    assert "for example," in doc.read_text(encoding="utf-8")


def test_fix_is_idempotent(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Use tools, e.g. Docker!\n", encoding="utf-8")
    fix_paths([tmp_path], write=True)
    second = fix_paths([tmp_path], write=True)
    assert not second[0].changed
