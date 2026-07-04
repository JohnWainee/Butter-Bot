from butter_bot.core import digest_facts, parse_sections, render_section, upsert_section


def test_append_creates_section():
    result = upsert_section("# Doc\n", "build", "Run make.", "sha256:abc")
    assert result.created
    sections = parse_sections(result.text)
    assert sections[0].name == "build"
    assert sections[0].body == "Run make."


def test_upsert_replaces_only_managed_body():
    doc = "# Doc\n\nHuman prose stays.\n"
    first = upsert_section(doc, "build", "Old body.", "sha256:a")
    second = upsert_section(first.text, "build", "New body.", "sha256:b")
    assert not second.created
    assert "Human prose stays." in second.text
    assert "Old body." not in second.text
    assert parse_sections(second.text)[0].body == "New body."


def test_human_edit_detected():
    first = upsert_section("# Doc\n", "build", "Original.", "sha256:a")
    tampered = first.text.replace("Original.", "Hand-edited.")
    second = upsert_section(tampered, "build", "Regenerated.", "sha256:b")
    assert second.human_edited


def test_untouched_body_not_flagged_as_human_edit():
    first = upsert_section("# Doc\n", "build", "Original.", "sha256:a")
    second = upsert_section(first.text, "build", "Regenerated.", "sha256:b")
    assert not second.human_edited


def test_multiple_sections_coexist():
    text = upsert_section("# Doc\n", "build", "Build body.", "sha256:a").text
    text = upsert_section(text, "run", "Run body.", "sha256:b").text
    names = [s.name for s in parse_sections(text)]
    assert names == ["build", "run"]


def test_digest_facts_is_order_independent():
    assert digest_facts({"a": 1, "b": 2}) == digest_facts({"b": 2, "a": 1})


def test_render_section_roundtrip():
    block = render_section("x", "Body text.", "sha256:facts")
    section = parse_sections(block)[0]
    assert section.facts_hash == "sha256:facts"
    assert section.body == "Body text."
