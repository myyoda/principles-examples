#!/usr/bin/env python3
"""build-pdf.py -- Scaffold for exporting YODA examples to PDF via pandoc.

Walks content/examples/, parses YAML front matter from each Markdown file,
groups examples by STAMPED principle, concatenates them into ordered Markdown,
and prints the pandoc command to produce a PDF.

This is a scaffold.  Look for TODO comments for planned enhancements.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# TODO: Replace this minimal parser with python-frontmatter for robustness.
def parse_front_matter(text: str) -> tuple[dict, str]:
    """Extract YAML front matter and body from a Markdown file.

    Returns a (metadata_dict, body_string) tuple.  The parser is intentionally
    minimal -- it handles the common ``---`` delimited front matter only.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text

    meta: dict = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            value = value.strip().strip('"').strip("'")
            # Primitive list detection (e.g. "[a, b, c]")
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            meta[key.strip()] = value

    return meta, match.group(2)


# Canonical ordering for STAMPED principles.
# Keys are the single-letter codes used in front matter; values are full names.
STAMPED_ORDER = ["S", "T", "A", "M", "P", "E", "D"]
STAMPED_NAMES = {
    "S": "Self-containment",
    "T": "Tracking",
    "A": "Actionability",
    "M": "Modularity",
    "P": "Portability",
    "E": "Ephemerality",
    "D": "Distributability",
}


def discover_examples(content_dir: Path) -> list[tuple[dict, str, Path]]:
    """Find all Markdown example files and return (meta, body, path) triples."""
    examples = []
    for md_path in sorted(content_dir.rglob("*.md")):
        # Skip Hugo section index files.
        if md_path.name == "_index.md":
            continue
        text = md_path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        examples.append((meta, body, md_path))
    return examples


def group_by_stamped(
    examples: list[tuple[dict, str, Path]],
) -> dict[str, list[tuple[dict, str, Path]]]:
    """Group examples by their primary STAMPED principle."""
    groups: dict[str, list[tuple[dict, str, Path]]] = {
        p: [] for p in STAMPED_ORDER
    }
    groups["Other"] = []

    for meta, body, path in examples:
        principles = meta.get("stamped_principles", [])
        if isinstance(principles, str):
            principles = [principles]

        placed = False
        for p in principles:
            letter = p.strip().upper()
            if letter in STAMPED_ORDER:
                groups[letter].append((meta, body, path))
                placed = True
                break
        if not placed:
            groups["Other"].append((meta, body, path))

    return groups


def build_combined_markdown(groups: dict[str, list[tuple[dict, str, Path]]]) -> str:
    """Concatenate grouped examples into a single Markdown document."""
    parts: list[str] = []
    parts.append("---")
    parts.append("title: STAMPED Principles Examples Collection")
    parts.append("---\n")

    for principle in STAMPED_ORDER + ["Other"]:
        entries = groups.get(principle, [])
        if not entries:
            continue

        name = STAMPED_NAMES.get(principle, principle)
        heading = f"{principle} -- {name}" if principle in STAMPED_NAMES else principle
        parts.append(f"# {heading}\n")

        for meta, body, path in entries:
            title = meta.get("title", path.stem.replace("-", " ").title())
            parts.append(f"## {title}\n")

            # TODO: Render tools / difficulty / verified metadata here.

            parts.append(body.strip())
            parts.append("\n\\newpage\n")

    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a combined Markdown file from YODA examples, "
        "grouped by STAMPED principle, ready for pandoc PDF export.",
    )
    parser.add_argument(
        "-c",
        "--content-dir",
        type=Path,
        default=Path("content/examples"),
        help="Path to the content/examples directory (default: content/examples)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("yoda-examples.md"),
        help="Output Markdown file path (default: yoda-examples.md)",
    )
    # TODO: Add --pdf flag to invoke pandoc directly via subprocess.
    args = parser.parse_args()

    if not args.content_dir.is_dir():
        print(f"Error: content directory not found: {args.content_dir}", file=sys.stderr)
        sys.exit(1)

    examples = discover_examples(args.content_dir)
    if not examples:
        print(f"Warning: no example files found under {args.content_dir}", file=sys.stderr)
        sys.exit(0)

    groups = group_by_stamped(examples)
    combined = build_combined_markdown(groups)

    args.output.write_text(combined, encoding="utf-8")
    print(f"Wrote combined Markdown to {args.output}  ({len(examples)} examples)")

    # Print pandoc instructions.
    pdf_path = args.output.with_suffix(".pdf")
    print()
    print("To produce a PDF, run:")
    print(f"  pandoc {args.output} -o {pdf_path} \\")
    print("    --pdf-engine=xelatex \\")
    print("    --toc \\")
    print("    -V geometry:margin=1in \\")
    print('    -V mainfont="DejaVu Serif" \\')
    print("    --highlight-style=tango")
    print()
    print("# TODO: Add --template option for a custom LaTeX template.")
    print("# TODO: Add --filter pandoc-citeproc if bibliography support is needed.")


if __name__ == "__main__":
    main()
