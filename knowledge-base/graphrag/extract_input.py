#!/usr/bin/env python3
"""Extract ALL text content from source repos for GraphRAG indexing.

Processes every readable text file. Binary files are skipped automatically.
Each source file becomes one text document with metadata header.
"""

import json
import os
import sys
from pathlib import Path

SOURCES_DIR = Path("knowledge-base/sources")
OUTPUT_DIR = Path("knowledge-base/graphrag/input")

# Skip dirs that are not useful
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv"}

# Binary extensions to skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".mp4", ".avi", ".mov", ".mp3", ".wav", ".flac",
    ".pdf", ".pptx", ".docx", ".xlsx",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".whl", ".egg", ".pyc", ".pyo",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".ttf", ".woff", ".woff2", ".eot",
    ".pkl", ".parquet", ".npy", ".npz", ".h5", ".hdf5",
    ".db", ".sqlite", ".sqlite3",
    ".DS_Store",
}

# Max single file size (1MB) - skip huge data files
MAX_FILE_SIZE = 1_000_000


def extract_notebook(path: Path) -> str:
    """Extract all cells from Jupyter notebook as text."""
    try:
        with open(path) as f:
            nb = json.load(f)
        parts = []
        for cell in nb.get("cells", []):
            cell_type = cell.get("cell_type", "")
            source = "".join(cell.get("source", []))
            if cell_type == "markdown":
                parts.append(source)
            elif cell_type == "code":
                parts.append(f"```\n{source}\n```")
        return "\n\n".join(parts)
    except Exception:
        return ""


def is_binary(path: Path) -> bool:
    """Check if file is binary by extension or content sampling."""
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True
    return False


def read_text_file(path: Path) -> str:
    """Read any text file, handling encoding issues."""
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""


def process_repo(repo_dir: Path, output_dir: Path):
    """Process ALL files in a repo into GraphRAG input documents."""
    repo_name = repo_dir.name
    doc_count = 0

    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)

        for fname in files:
            fpath = root_path / fname

            # Skip large files
            try:
                size = fpath.stat().st_size
                if size > MAX_FILE_SIZE or size == 0:
                    continue
            except OSError:
                continue

            # Skip binary
            if is_binary(fpath):
                continue

            # Extract content
            suffix = fpath.suffix.lower()
            if suffix == ".ipynb":
                content = extract_notebook(fpath)
            else:
                content = read_text_file(fpath)

            if not content or len(content.strip()) < 20:
                continue

            # Create document with metadata header
            rel_path = fpath.relative_to(SOURCES_DIR)
            header = f"Source: {rel_path}\nRepo: {repo_name}\nFile: {fname}\n\n"

            doc_name = str(rel_path).replace("/", "__").replace("\\", "__")
            doc_name = doc_name[:200]
            out_path = output_dir / f"{doc_name}.txt"

            out_path.write_text(header + content)
            doc_count += 1

    return doc_count


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clean previous output
    for f in OUTPUT_DIR.glob("*.txt"):
        f.unlink()

    total = 0
    for repo_dir in sorted(SOURCES_DIR.iterdir()):
        if repo_dir.is_dir() and not repo_dir.name.startswith("."):
            count = process_repo(repo_dir, OUTPUT_DIR)
            print(f"  {repo_dir.name}: {count} documents")
            total += count

    print(f"\nTotal: {total} documents extracted to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
