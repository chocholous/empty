#!/usr/bin/env python3
"""Extract text content from source repos for GraphRAG indexing.

Smart filtering: includes only knowledge-valuable files, skips
machine-generated definitions, test data, build configs, and binaries.
Each source file becomes one text document with metadata header.
"""

import json
import os
import sys
from pathlib import Path

SOURCES_DIR = Path("knowledge-base/sources")
OUTPUT_DIR = Path("knowledge-base/graphrag/input")

# --- FILTERING RULES ---

# Dirs to always skip
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    ".vscode", ".idea", ".github", "dist", "build", ".next",
    ".tox", ".mypy_cache", ".pytest_cache", "coverage",
}

# Extensions to INCLUDE (knowledge-valuable)
INCLUDE_EXTENSIONS = {
    # Documentation (highest value)
    ".md", ".mdx", ".rst", ".txt", ".ipynb",
    # Code (implementation patterns)
    ".py", ".ts", ".tsx", ".js", ".jsx", ".cs", ".csx",
    # Infrastructure-as-code (deployment patterns)
    ".bicep", ".tf", ".sh", ".ps1", ".bash",
    # Config examples (when not in skip lists)
    ".yaml", ".yml",
}

# Filenames to ALWAYS SKIP regardless of extension
SKIP_FILENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "composer.lock", "Gemfile.lock", "poetry.lock",
    ".gitignore", ".gitattributes", ".editorconfig",
    ".eslintrc.json", ".prettierrc", ".prettierrc.json",
    "tsconfig.json", "jest.config.js", "jest.config.ts",
    ".npmrc", ".nvmrc", ".node-version",
    "thumbs.db", ".ds_store",
}

# Filenames to ALWAYS INCLUDE (high value, even if extension not in list)
INCLUDE_FILENAMES = {
    "skill.md", "agents.md", "claude.md", "copilot-instructions.md",
    "manifest.json", "declarativeagent.json",
    "sample.json", "samples.json",
}

# Path patterns to skip (substring match on relative path)
SKIP_PATH_PATTERNS = [
    "/test/", "/tests/", "/__tests__/",
    "/spec/", "/.github/workflows/",
    "/node_modules/", "/coverage/",
]

# Specific large-volume low-value files
SKIP_SPECIFIC_FILENAMES = {
    "apidefinition.swagger.json",
    "apiproperties.json",
}

# Binary extensions
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
    # Additional: generated/data
    ".map", ".min.js", ".min.css",
    ".csv", ".tsv",
    ".xsd", ".xsl", ".xslt",
    ".css", ".scss", ".less",
    ".html", ".htm",
    ".csproj", ".sln", ".props",
    ".xml",
}

# Max single file size (500KB)
MAX_FILE_SIZE = 500_000


def should_include(fpath: Path, rel_path_str: str) -> bool:
    """Decide if a file should be included based on smart filtering."""
    fname_lower = fpath.name.lower()
    suffix = fpath.suffix.lower()

    # Always skip specific low-value filenames
    if fname_lower in SKIP_SPECIFIC_FILENAMES:
        return False
    if fname_lower in SKIP_FILENAMES:
        return False

    # Always include high-value filenames
    if fname_lower in INCLUDE_FILENAMES:
        return True

    # Skip binary
    if suffix in BINARY_EXTENSIONS:
        return False

    # Skip test paths
    rel_lower = rel_path_str.lower()
    for pattern in SKIP_PATH_PATTERNS:
        if pattern in rel_lower:
            return False

    # Include by extension
    if suffix in INCLUDE_EXTENSIONS:
        return True

    # Skip everything else (unknown extensions, .json without special name, etc.)
    return False


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


def read_text_file(path: Path) -> str:
    """Read any text file, handling encoding issues."""
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""


def process_repo(repo_dir: Path, output_dir: Path):
    """Process filtered files in a repo into GraphRAG input documents."""
    repo_name = repo_dir.name
    doc_count = 0
    skip_count = 0

    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)

        for fname in files:
            fpath = root_path / fname
            rel_path = fpath.relative_to(SOURCES_DIR)
            rel_path_str = str(rel_path)

            # Size check
            try:
                size = fpath.stat().st_size
                if size > MAX_FILE_SIZE or size == 0:
                    skip_count += 1
                    continue
            except OSError:
                continue

            # Smart filter
            if not should_include(fpath, rel_path_str):
                skip_count += 1
                continue

            # Binary content check (null bytes)
            if fpath.suffix.lower() != ".ipynb":
                try:
                    with open(fpath, "rb") as f:
                        chunk = f.read(8192)
                        if b"\x00" in chunk:
                            skip_count += 1
                            continue
                except Exception:
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
            header = f"Source: {rel_path}\nRepo: {repo_name}\nFile: {fname}\n\n"

            doc_name = str(rel_path).replace("/", "__").replace("\\", "__")
            doc_name = doc_name[:200]
            out_path = output_dir / f"{doc_name}.txt"

            out_path.write_text(header + content)
            doc_count += 1

    return doc_count, skip_count


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clean previous output
    for f in OUTPUT_DIR.glob("*.txt"):
        f.unlink()

    total = 0
    total_skipped = 0
    for repo_dir in sorted(SOURCES_DIR.iterdir()):
        if repo_dir.is_dir() and not repo_dir.name.startswith("."):
            count, skipped = process_repo(repo_dir, OUTPUT_DIR)
            print(f"  {repo_dir.name}: {count} docs ({skipped} skipped)")
            total += count
            total_skipped += skipped

    print(f"\nTotal: {total} documents extracted ({total_skipped} skipped)")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
