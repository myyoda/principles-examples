"""Shared parsing utilities for shell script snippets in Markdown examples.

Extracts fenced ``sh``/``bash`` code blocks and their ``# pragma:`` annotations.
Used by both ``conftest.py`` (Sybil test runner) and ``materialize_examples``
(branch materializer).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, NamedTuple

# Regex: fenced code block with sh or bash language tag.
# Captures the code content between the opening and closing fences.
FENCE_RE = re.compile(
    r"^```(?:sh|bash)\s*\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)


def parse_pragmas(code: str) -> dict[str, str | list[str]]:
    """Extract ``# pragma: key value`` directives from script text.

    Most keys map to a single string value.  ``materialize`` may appear
    multiple times and is always returned as a list.
    """
    pragmas: dict[str, str | list[str]] = {}
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("# pragma:"):
            # e.g. "# pragma: testrun scenario-1"
            parts = stripped.split(None, 3)  # ['#', 'pragma:', key, value...]
            if len(parts) >= 3:
                key = parts[2]
                value = parts[3] if len(parts) > 3 else ""
                if key == "materialize":
                    pragmas.setdefault("materialize", [])
                    assert isinstance(pragmas["materialize"], list)
                    pragmas["materialize"].append(value)
                else:
                    pragmas[key] = value
    return pragmas


class ScriptBlock(NamedTuple):
    """A fenced shell code block extracted from a Markdown file."""

    code: str
    pragmas: dict[str, str | list[str]]
    file_stem: str


def iter_script_blocks(md_path: str | Path) -> Iterator[ScriptBlock]:
    """Yield :class:`ScriptBlock` instances from a Markdown file.

    Only blocks containing ``# pragma: testrun`` are yielded.
    """
    md_path = Path(md_path)
    text = md_path.read_text(encoding="utf-8")
    file_stem = md_path.stem
    for m in FENCE_RE.finditer(text):
        code = m.group(1)
        if "# pragma: testrun" not in code:
            continue
        pragmas = parse_pragmas(code)
        yield ScriptBlock(code=code, pragmas=pragmas, file_stem=file_stem)
