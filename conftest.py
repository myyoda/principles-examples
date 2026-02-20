"""sybil conftest: test shell script snippets embedded in Markdown examples.

Code blocks annotated with ``# pragma: testrun`` are extracted and executed.
See the plan at .claude/plans/ for the full annotation format.
"""
from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import tempfile

import pytest
from sybil import Document, Region, Sybil

# Regex: fenced code block with sh or bash language tag.
# Captures the code content between the opening and closing fences.
_FENCE_RE = re.compile(
    r"^```(?:sh|bash)\s*\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)


def _parse_pragmas(code: str) -> dict[str, str]:
    """Extract ``# pragma: key value`` directives from script text."""
    pragmas: dict[str, str] = {}
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("# pragma:"):
            # e.g. "# pragma: testrun scenario-1"
            parts = stripped.split(None, 3)  # ['#', 'pragma:', key, value...]
            if len(parts) >= 3:
                key = parts[2]
                value = parts[3] if len(parts) > 3 else ""
                pragmas[key] = value
    return pragmas


def shell_script_parser(document: Document):
    """Find ``sh`` code blocks containing ``# pragma: testrun`` and yield Regions."""
    for m in _FENCE_RE.finditer(document.text):
        code = m.group(1)
        if "# pragma: testrun" not in code:
            continue
        pragmas = _parse_pragmas(code)
        yield Region(
            start=m.start(),
            end=m.end(),
            parsed={"code": code, "pragmas": pragmas},
            evaluator=evaluate_shell_script,
        )


def evaluate_shell_script(example):
    """Run a shell script extracted from markdown and check it succeeds."""
    code = example.parsed["code"]
    pragmas = example.parsed["pragmas"]

    # Check tool requirements
    requires = pragmas.get("requires", "sh").split()
    missing = [t for t in requires if not shutil.which(t)]
    if missing:
        pytest.skip(f"missing: {', '.join(missing)}")

    timeout = int(pragmas.get("timeout", "60"))
    test_id = pragmas.get("testrun", "unnamed")

    # Write to temp file and execute
    fd, path = tempfile.mkstemp(suffix=".sh", prefix=f"sybil-{test_id}-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        result = subprocess.run(
            ["sh", path],
            timeout=timeout,
        )
        expected_rc = int(pragmas.get("exitcode", "0"))
        if result.returncode != expected_rc:
            raise AssertionError(
                f"Script {test_id} exited with code {result.returncode}"
                f" (expected {expected_rc})"
            )
    except subprocess.TimeoutExpired:
        raise AssertionError(f"Script {test_id} timed out after {timeout}s")
    finally:
        os.unlink(path)


pytest_collect_file = Sybil(
    parsers=[shell_script_parser],
    patterns=["content/examples/*.md"],
).pytest()
