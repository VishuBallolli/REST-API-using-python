"""File-operation helpers for text, CSV, and JSON files.

This module contains filesystem helper functions only. FastAPI request models
and API routes belong in main.py, not in this module.
"""

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


# Project directories
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure the directories exist.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Shared validation/path helpers
# ---------------------------------------------------------------------------
def _get_target_dir(directory: str) -> Path:
    """Return an allowed directory or raise ValueError for invalid input."""
    if directory == "uploads":
        return UPLOAD_DIR
    if directory == "reports":
        return REPORTS_DIR
    raise ValueError("directory must be either 'uploads' or 'reports'")


def _get_file_path(filename: str, directory: str = "uploads") -> Path:
    """Build a safe path for a single filename inside an allowed directory."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("filename must be a non-empty string")

    # Only accept a filename, not a path. This blocks ../, absolute paths,
    # and Windows path separators from escaping the chosen directory.
    if filename in {".", ".."} or Path(filename).name != filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename: provide a filename without directory paths")

    target_dir = _get_target_dir(directory).resolve()
    file_path = (target_dir / filename).resolve()

    # Additional containment check, including symlink resolution.
    try:
        file_path.relative_to(target_dir)
    except ValueError as exc:
        raise ValueError("Invalid file path") from exc

    return file_path


def _error(message: str) -> dict:
    return {"success": False, "error": message}


# ---------------------------------------------------------------------------
# Text file operations
# ---------------------------------------------------------------------------
def create_text_file(filename: str, content: str, directory: str = "uploads") -> dict:
    """Create a new UTF-8 text file without overwriting an existing file."""
    try:
        file_path = _get_file_path(filename, directory)
        if file_path.exists():
            return _error(f"File '{filename}' already exists")

        # x mode makes creation exclusive, preventing accidental overwrite.
        with file_path.open("x", encoding="utf-8") as file:
            file.write(content)

        return {
            "success": True,
            "message": f"File '{filename}' created successfully",
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }
    except FileExistsError:
        return _error(f"File '{filename}' already exists")
    except PermissionError:
        return _error("Permission denied - cannot write to directory")
    except Exception as exc:
        return _error(f"Error creating file: {exc}")


def write_text_file(filename: str, content: str, directory: str = "uploads") -> dict:
    """Write UTF-8 content to a file, overwriting it if it exists."""
    try:
        file_path = _get_file_path(filename, directory)
        with file_path.open("w", encoding="utf-8") as file:
            file.write(content)
        return {
            "success": True,
            "message": f"Content written to '{filename}'",
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _error(f"Error writing file: {exc}")


def append_text_file(filename: str, content: str, directory: str = "uploads") -> dict:
    """Append UTF-8 content to a file (creating it if necessary)."""
    try:
        file_path = _get_file_path(filename, directory)
        with file_path.open("a", encoding="utf-8") as file:
            file.write(content)
        return {
            "success": True,
            "message": f"Content appended to '{filename}'",
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _error(f"Error appending to file: {exc}")


def read_text_file(filename: str, directory: str = "uploads") -> dict:
    """Read a whole UTF-8 text file and return its content and metadata."""
    try:
        file_path = _get_file_path(filename, directory)
        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        content = file_path.read_text(encoding="utf-8")
        return {
            "success": True,
            "filename": filename,
            "content": content,
            "size": file_path.stat().st_size,
            "lines": len(content.splitlines()),
        }
    except Exception as exc:
        return _error(f"Error reading file: {exc}")


def read_text_file_lines(filename: str, directory: str = "uploads") -> dict:
    """Read a text file as a list of lines, trimming line-ending whitespace."""
    try:
        file_path = _get_file_path(filename, directory)
        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        with file_path.open("r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines()]
        return {
            "success": True,
            "filename": filename,
            "lines": lines,
            "line_count": len(lines),
        }
    except Exception as exc:
        return _error(f"Error reading file: {exc}")


def check_file_exists(filename: str, directory: str = "uploads") -> dict:
    """Check whether a path exists and return basic file metadata."""
    try:
        file_path = _get_file_path(filename, directory)
        if file_path.exists():
            stats = file_path.stat()
            return {
                "success": True,
                "exists": True,
                "filename": filename,
                "size": stats.st_size,
                "modified": stats.st_mtime,
                "is_file": file_path.is_file(),
            }
        return {"success": True, "exists": False, "filename": filename}
    except Exception as exc:
        return _error(f"Error checking file: {exc}")


def rename_file(old_name: str, new_name: str, directory: str = "uploads") -> dict:
    """Rename a file within the selected directory."""
    try:
        old_path = _get_file_path(old_name, directory)
        new_path = _get_file_path(new_name, directory)

        if not old_path.is_file():
            return _error(f"File '{old_name}' not found")
        if new_path.exists():
            return _error(f"File '{new_name}' already exists")

        old_path.rename(new_path)
        return {
            "success": True,
            "message": f"File renamed from '{old_name}' to '{new_name}'",
        }
    except Exception as exc:
        return _error(f"Error renaming file: {exc}")


def copy_file(filename: str, new_name: str, directory: str = "uploads") -> dict:
    """Copy a file to a new name in the same selected directory."""
    try:
        source_path = _get_file_path(filename, directory)
        dest_path = _get_file_path(new_name, directory)

        if not source_path.is_file():
            return _error(f"File '{filename}' not found")
        if dest_path.exists():
            return _error(f"File '{new_name}' already exists")

        shutil.copy2(source_path, dest_path)
        return {
            "success": True,
            "message": f"File copied from '{filename}' to '{new_name}'",
            "size": dest_path.stat().st_size,
        }
    except Exception as exc:
        return _error(f"Error copying file: {exc}")


def delete_file(filename: str, directory: str = "uploads") -> dict:
    """Delete a file inside the selected directory."""
    try:
        file_path = _get_file_path(filename, directory)
        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        file_path.unlink()
        return {"success": True, "message": f"File '{filename}' deleted successfully"}
    except Exception as exc:
        return _error(f"Error deleting file: {exc}")


def get_file_size(filename: str, directory: str = "uploads") -> dict:
    """Return a file's size in bytes, KB, and MB."""
    try:
        file_path = _get_file_path(filename, directory)
        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        size_bytes = file_path.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        return {
            "success": True,
            "filename": filename,
            "size_bytes": size_bytes,
            "size_kb": round(size_kb, 2),
            "size_mb": round(size_mb, 2),
        }
    except Exception as exc:
        return _error(f"Error getting file size: {exc}")


# ---------------------------------------------------------------------------
# CSV file operations
# ---------------------------------------------------------------------------
def read_csv_file(filename: str, directory: str = "uploads") -> dict:
    """Read a CSV file as a list of dictionaries using its header row."""
    try:
        file_path = _get_file_path(filename, directory)
        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        with file_path.open("r", newline="", encoding="utf-8") as file:
            data = list(csv.DictReader(file))
        return {"success": True, "filename": filename, "row_count": len(data), "data": data}
    except Exception as exc:
        return _error(f"Error reading CSV: {exc}")


def write_csv_file(filename: str, data: List[Dict], directory: str = "reports") -> dict:
    """Write dictionaries to a CSV file, using the first row's keys as headers."""
    try:
        if not data:
            return _error("No data provided to write")

        file_path = _get_file_path(filename, directory)
        headers = list(data[0].keys())
        with file_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        return {
            "success": True,
            "message": f"CSV file '{filename}' created successfully",
            "path": str(file_path),
            "rows": len(data),
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _error(f"Error writing CSV: {exc}")


# ---------------------------------------------------------------------------
# JSON file operations
# ---------------------------------------------------------------------------
def read_json_file(filename: str, directory: str = "uploads") -> dict:
    """Read and parse a JSON file."""
    try:
        file_path = _get_file_path(filename, directory)
        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return {"success": True, "filename": filename, "data": data}
    except json.JSONDecodeError as exc:
        return _error(f"Invalid JSON format: {exc}")
    except Exception as exc:
        return _error(f"Error reading JSON: {exc}")


def write_json_file(filename: str, data: Any, directory: str = "reports") -> dict:
    """Write a Python value to a formatted UTF-8 JSON file."""
    try:
        file_path = _get_file_path(filename, directory)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return {
            "success": True,
            "message": f"JSON file '{filename}' created successfully",
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _error(f"Error writing JSON: {exc}")


# This module deliberately contains no FastAPI routes or Pydantic models.
if __name__ == "__main__":
    print("Testing File Operations")
    print("=" * 50)

    print("\n1. Creating text file...")
    result = create_text_file("test.txt", "Hello, World!\n")
    print(result)

    print("\n2. Reading text file...")
    result = read_text_file("test.txt")
    print(f"Content: {result.get('content', 'N/A')}")

    print("\n3. Checking file exists...")
    result = check_file_exists("test.txt")
    print(f"Exists: {result.get('exists', False)}")

    print("\n" + "=" * 50)
    print("Testing complete!")
