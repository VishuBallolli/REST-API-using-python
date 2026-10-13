
"""File-operation helpers for text, CSV, and JSON files.

This module contains filesystem helper functions only.
FastAPI routes and Pydantic models belong in main.py.
"""

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Project directories
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Shared validation and error helpers
# ---------------------------------------------------------------------------

def _get_target_dir(directory: str) -> Path:
    """Return an approved directory."""
    if directory == "uploads":
        return UPLOAD_DIR

    if directory == "reports":
        return REPORTS_DIR

    raise ValueError("directory must be either 'uploads' or 'reports'")


def _get_file_path(filename: str, directory: str = "uploads") -> Path:
    """Validate a filename and keep it inside an approved directory."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("filename must be a non-empty string")

    # Reject paths, traversal attempts, and Windows path separators.
    if (
        filename in {".", ".."}
        or Path(filename).name != filename
        or "/" in filename
        or "\\" in filename
    ):
        raise ValueError(
            "Invalid filename: provide a filename without directory paths"
        )

    target_dir = _get_target_dir(directory).resolve()
    file_path = (target_dir / filename).resolve()

    # Ensure the resolved path remains inside the approved directory.
    try:
        file_path.relative_to(target_dir)
    except ValueError as exc:
        raise ValueError("Invalid file path") from exc

    return file_path


def _error(message: str) -> dict:
    """Return a consistent error result."""
    return {"success": False, "error": message}


def _handle_file_error(action: str, exc: Exception) -> dict:
    """Return a clear error without exposing internal filesystem paths."""
    if isinstance(exc, FileExistsError):
        return _error("File already exists")

    if isinstance(exc, FileNotFoundError):
        return _error("File or directory not found")

    if isinstance(exc, PermissionError):
        return _error("Permission denied")

    if isinstance(exc, IsADirectoryError):
        return _error("The requested path is a directory, not a file")

    if isinstance(exc, ValueError):
        return _error(str(exc))

    return _error(f"Unable to {action}")


# ---------------------------------------------------------------------------
# Text file operations
# ---------------------------------------------------------------------------

def create_text_file(
    filename: str, content: str, directory: str = "uploads"
) -> dict:
    """Create a new text file without overwriting an existing file."""
    try:
        file_path = _get_file_path(filename, directory)

        # Exclusive creation prevents overwriting an existing file.
        with file_path.open("x", encoding="utf-8") as file:
            file.write(content)

        return {
            "success": True,
            "message": f"File '{filename}' created successfully",
            "filename": filename,
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _handle_file_error("create the file", exc)


def write_text_file(
    filename: str, content: str, directory: str = "uploads"
) -> dict:
    """Write text to a file, replacing its existing contents if present."""
    try:
        file_path = _get_file_path(filename, directory)

        with file_path.open("w", encoding="utf-8") as file:
            file.write(content)

        return {
            "success": True,
            "message": f"Content written to '{filename}'",
            "filename": filename,
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _handle_file_error("write the file", exc)


def append_text_file(
    filename: str, content: str, directory: str = "uploads"
) -> dict:
    """Append text to a file, creating it if necessary."""
    try:
        file_path = _get_file_path(filename, directory)

        with file_path.open("a", encoding="utf-8") as file:
            file.write(content)

        return {
            "success": True,
            "message": f"Content appended to '{filename}'",
            "filename": filename,
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _handle_file_error("append to the file", exc)


def read_text_file(filename: str, directory: str = "uploads") -> dict:
    """Read a complete UTF-8 text file."""
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
        return _handle_file_error("read the file", exc)


def read_text_file_lines(
    filename: str, directory: str = "uploads"
) -> dict:
    """Read a text file as a list of lines."""
    try:
        file_path = _get_file_path(filename, directory)

        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        with file_path.open("r", encoding="utf-8") as file:
            lines = [line.rstrip("\r\n") for line in file]

        return {
            "success": True,
            "filename": filename,
            "lines": lines,
            "line_count": len(lines),
        }
    except Exception as exc:
        return _handle_file_error("read the file", exc)


def check_file_exists(filename: str, directory: str = "uploads") -> dict:
    """Check whether a path exists and return basic file metadata."""
    try:
        file_path = _get_file_path(filename, directory)

        if not file_path.exists():
            return {
                "success": True,
                "exists": False,
                "filename": filename,
            }

        stats = file_path.stat()

        return {
            "success": True,
            "exists": True,
            "filename": filename,
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "is_file": file_path.is_file(),
        }
    except Exception as exc:
        return _handle_file_error("check the file", exc)


def rename_file(
    old_name: str, new_name: str, directory: str = "uploads"
) -> dict:
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
        return _handle_file_error("rename the file", exc)


def copy_file(
    filename: str, new_name: str, directory: str = "uploads"
) -> dict:
    """Copy a file to a new name in the same directory."""
    try:
        source_path = _get_file_path(filename, directory)
        dest_path = _get_file_path(new_name, directory)

        if not source_path.is_file():
            return _error(f"File '{filename}' not found")

        if dest_path.exists():
            return _error(f"File '{new_name}' already exists")

        # Exclusive destination creation prevents overwriting a file.
        with source_path.open("rb") as source:
            with dest_path.open("xb") as destination:
                shutil.copyfileobj(source, destination)

        return {
            "success": True,
            "message": f"File copied from '{filename}' to '{new_name}'",
            "size": dest_path.stat().st_size,
        }
    except Exception as exc:
        return _handle_file_error("copy the file", exc)


def delete_file(filename: str, directory: str = "uploads") -> dict:
    """Delete a file inside the selected directory."""
    try:
        file_path = _get_file_path(filename, directory)

        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        file_path.unlink()

        return {
            "success": True,
            "message": f"File '{filename}' deleted successfully",
        }
    except Exception as exc:
        return _handle_file_error("delete the file", exc)


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
        return _handle_file_error("get the file size", exc)


# ---------------------------------------------------------------------------
# CSV file operations
# ---------------------------------------------------------------------------

def read_csv_file(filename: str, directory: str = "uploads") -> dict:
    """Read a CSV file as dictionaries using its header row."""
    try:
        file_path = _get_file_path(filename, directory)

        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        with file_path.open("r", newline="", encoding="utf-8-sig") as file:
            data = list(csv.DictReader(file))

        return {
            "success": True,
            "filename": filename,
            "row_count": len(data),
            "data": data,
        }
    except Exception as exc:
        return _handle_file_error("read the CSV file", exc)


def write_csv_file(
    filename: str,
    data: List[Dict],
    directory: str = "reports",
) -> dict:
    """Create a CSV file without overwriting an existing file."""
    try:
        if not data:
            return _error("No data provided to write")

        if not all(isinstance(row, dict) for row in data):
            return _error("Each CSV row must be a dictionary")

        headers = list(data[0].keys())

        if not headers:
            return _error("CSV data must contain at least one column")

        if any(set(row.keys()) != set(headers) for row in data):
            return _error("All CSV rows must have the same columns")

        file_path = _get_file_path(filename, directory)

        # "x" creates a new file and fails if it already exists.
        with file_path.open("x", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        return {
            "success": True,
            "message": f"CSV file '{filename}' created successfully",
            "filename": filename,
            "rows": len(data),
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _handle_file_error("create the CSV file", exc)


# ---------------------------------------------------------------------------
# JSON file operations
# ---------------------------------------------------------------------------

def read_json_file(filename: str, directory: str = "uploads") -> dict:
    """Read and parse a JSON file."""
    try:
        file_path = _get_file_path(filename, directory)

        if not file_path.is_file():
            return _error(f"File '{filename}' not found")

        with file_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        return {
            "success": True,
            "filename": filename,
            "data": data,
        }
    except json.JSONDecodeError:
        return _error("Invalid JSON format")
    except Exception as exc:
        return _handle_file_error("read the JSON file", exc)


def write_json_file(
    filename: str,
    data: Any,
    directory: str = "reports",
) -> dict:
    """Create a JSON file without overwriting an existing file."""
    try:
        file_path = _get_file_path(filename, directory)

        # "x" prevents overwriting an existing JSON file.
        with file_path.open("x", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )

        return {
            "success": True,
            "message": f"JSON file '{filename}' created successfully",
            "filename": filename,
            "size": file_path.stat().st_size,
        }
    except Exception as exc:
        return _handle_file_error("create the JSON file", exc)


# This module contains no FastAPI routes or Pydantic models.
if __name__ == "__main__":
    print("Testing File Operations")
    print("=" * 50)

    print("\n1. Creating text file...")
    result = create_text_file("test.txt", "Hello, World!\n")
    print(result)

    print("\n2. Reading text file...")
    result = read_text_file("test.txt")
    print(f"Content: {result.get('content', 'N/A')}")

    print("\n3. Checking whether the file exists...")
    result = check_file_exists("test.txt")
    print(f"Exists: {result.get('exists', False)}")

    print("\n" + "=" * 50)
    print("Testing complete!")
