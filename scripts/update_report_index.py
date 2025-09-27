#!/usr/bin/env python3
"""Update the report index with a link to the branch report."""
from __future__ import annotations

import argparse
import pathlib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=pathlib.Path, required=True, help="Path to the index HTML file.")
    parser.add_argument("--branch", required=True, help="Branch name to add to the index.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index_path: pathlib.Path = args.index
    branch: str = args.branch

    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")

    link_html = f'  <li><a href="{branch}/index.html">{branch}</a></li>'

    text = index_path.read_text()
    if link_html in text:
        return

    if "</ul>" not in text:
        raise ValueError("Index file must contain a </ul> tag to insert branch links.")

    updated = text.replace("</ul>", f"{link_html}\n</ul>")
    index_path.write_text(updated)


if __name__ == "__main__":
    main()
