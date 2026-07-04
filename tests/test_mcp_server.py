from pathlib import Path

from butter_bot.mcp import server


def test_tools_are_registered():
    tools = server.app._tool_manager.list_tools()
    names = {t.name for t in tools}
    assert {"lint_style", "apply_style_fixes"} <= names


def test_lint_style_tool(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Use tools, e.g. Docker!\n", encoding="utf-8")
    result = server.lint_style([str(doc)])
    assert result["errors"] >= 2


def test_apply_style_fixes_tool(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("The doc is written by the bot, e.g. this one!\n", encoding="utf-8")
    result = server.apply_style_fixes([str(doc)])
    assert result["files_changed"] == [str(doc)]
    assert any(item["rule_id"] == "passive-voice" for item in result["drafting_brief"])
    assert "for example," in doc.read_text(encoding="utf-8")
