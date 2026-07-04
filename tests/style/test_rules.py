from butter_bot.style import Severity, lint_text


def rule_ids(text: str) -> list[str]:
    return [v.rule_id for v in lint_text(text)]


def test_latin_abbreviations_flagged():
    ids = rule_ids("Use containers, e.g. Docker, or VMs, i.e. heavier ones, etc.")
    assert ids.count("latin-abbreviation") == 3


def test_latin_abbreviation_is_error():
    violations = lint_text("Use tools, e.g. Docker.")
    latin = [v for v in violations if v.rule_id == "latin-abbreviation"]
    assert latin[0].severity is Severity.ERROR
    assert latin[0].autofixable


def test_exclamation_flagged():
    assert "exclamation" in rule_ids("This is great!")


def test_image_syntax_not_flagged_as_exclamation():
    assert "exclamation" not in rule_ids("See ![diagram](docs/diagram.png) for details.")


def test_serial_comma_flagged():
    assert "serial-comma" in rule_ids("Install docker, compose and kubectl before you start.")


def test_serial_comma_present_not_flagged():
    assert "serial-comma" not in rule_ids("Install docker, compose, and kubectl.")


def test_link_text_flagged():
    assert "link-text" in rule_ids("For details, [click here](https://example.com).")


def test_descriptive_link_text_not_flagged():
    assert "link-text" not in rule_ids("See the [project plan](docs/plan.md).")


def test_heading_title_case_flagged():
    assert "heading-case" in rule_ids("# Getting Started Guide")


def test_heading_sentence_case_not_flagged():
    assert "heading-case" not in rule_ids("# Getting started with the CLI")


def test_heading_capital_after_colon_not_flagged():
    assert "heading-case" not in rule_ids("# ADR 001: Shared core with frontends")


def test_heading_capital_after_dash_not_flagged():
    assert "heading-case" not in rule_ids("### M0 — Scaffold the repository")


def test_passive_voice_flagged():
    assert "passive-voice" in rule_ids("The file is written by the generator.")


def test_sentence_length_flagged():
    long_sentence = "This sentence " + "really " * 20 + "never ends."
    assert "sentence-length" in rule_ids(long_sentence)


def test_code_blocks_skipped():
    text = "```bash\necho 'e.g. this is code!'\n```\n"
    assert rule_ids(text) == []


def test_inline_code_masked():
    assert "exclamation" not in rule_ids("Run `make lint!` to check the docs.")
