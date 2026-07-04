"""Line-aware markdown segmentation for the style engine.

The segmenter classifies each line and masks non-prose spans (inline code,
link targets) with spaces so that rule regexes keep correct column numbers.
"""

import re
from dataclasses import dataclass

_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK_TARGET = re.compile(r"\]\(([^)]*)\)")
_HTML_COMMENT = re.compile(r"<!--.*?-->")


@dataclass
class Line:
    """One classified source line."""

    number: int  # 1-based
    raw: str
    text: str  # prose with code spans and link targets masked
    kind: str  # "prose" | "heading" | "table" | "skip"


def _mask(match: re.Match) -> str:
    return " " * len(match.group(0))


def _mask_line(raw: str) -> str:
    text = _INLINE_CODE.sub(_mask, raw)
    text = _HTML_COMMENT.sub(_mask, text)
    return _LINK_TARGET.sub(lambda m: "]" + " " * (len(m.group(0)) - 1), text)


def segment(source: str) -> list[Line]:
    """Classify every line of a markdown document."""
    lines: list[Line] = []
    in_fence = False
    for number, raw in enumerate(source.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            lines.append(Line(number, raw, "", "skip"))
            continue
        if in_fence or not stripped:
            lines.append(Line(number, raw, "", "skip"))
            continue
        if stripped.startswith("#"):
            lines.append(Line(number, raw, _mask_line(raw), "heading"))
            continue
        if stripped.startswith("|") or stripped.startswith("<!--"):
            lines.append(Line(number, raw, _mask_line(raw), "table"))
            continue
        lines.append(Line(number, raw, _mask_line(raw), "prose"))
    return lines


@dataclass
class Sentence:
    """One sentence assembled from consecutive prose lines."""

    line: int  # 1-based line where the sentence starts
    text: str


_SENTENCE_END = re.compile(r"(?<=[.?!])\s+")


def sentences(lines: list[Line]) -> list[Sentence]:
    """Assemble sentences from paragraphs of prose lines."""
    result: list[Sentence] = []
    paragraph: list[Line] = []

    def flush() -> None:
        if not paragraph:
            return
        joined = " ".join(ln.text.strip() for ln in paragraph)
        start = paragraph[0].number
        for chunk in _SENTENCE_END.split(joined):
            chunk = chunk.strip()
            if chunk:
                result.append(Sentence(start, chunk))
        paragraph.clear()

    for line in lines:
        if line.kind == "prose":
            paragraph.append(line)
        else:
            flush()
    flush()
    return result
