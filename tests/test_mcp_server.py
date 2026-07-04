from pathlib import Path

from butter_bot.mcp import server


def test_tools_are_registered():
    tools = server.app._tool_manager.list_tools()
    names = {t.name for t in tools}
    expected = {
        "lint_style",
        "apply_style_fixes",
        "scan_repo",
        "extract_facts",
        "plan_doc",
        "write_managed_doc",
    }
    assert expected <= names


def test_scan_repo_tool(fixture_repo: Path):
    result = server.scan_repo(str(fixture_repo))
    assert set(result["ecosystems"]) == {"python", "shell", "dockerfile", "compose"}


def test_plan_doc_tool(fixture_repo: Path):
    result = server.plan_doc(str(fixture_repo), "runbook")
    assert result["target_path"] == "docs/runbook.md"
    assert result["sections"]


def test_plan_doc_rejects_unknown_type(fixture_repo: Path):
    assert "error" in server.plan_doc(str(fixture_repo), "novel")


def test_write_managed_doc_roundtrip(fixture_repo: Path):
    result = server.write_managed_doc(
        str(fixture_repo), "docs/runbook.md", "build", "Run the build.", "sha256:x", "Runbook"
    )
    assert result["written"] and result["created_section"]
    text = (fixture_repo / "docs" / "runbook.md").read_text(encoding="utf-8")
    assert text.startswith("# Runbook")
    assert "Run the build." in text


def test_write_managed_doc_rejects_style_errors(fixture_repo: Path):
    result = server.write_managed_doc(
        str(fixture_repo), "docs/runbook.md", "build", "Build it, e.g. with make!", "sha256:x"
    )
    assert not result["written"]
    assert result["violations"]


def test_write_managed_doc_rejects_escape(fixture_repo: Path):
    result = server.write_managed_doc(
        str(fixture_repo), "../outside.md", "build", "Body.", "sha256:x"
    )
    assert not result["written"]


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
