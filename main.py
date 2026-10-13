
# main.py
"""Entry point for the Employee Management FastAPI application."""

from pathlib import Path
from typing import Any, Optional

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

import employee_queries
import file_operations


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


app = FastAPI(
    title="Employee Management API",
    description="A REST API for managing employee records with MySQL database",
    version="1.0.0",
)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class EmployeeCreate(BaseModel):
    """Request schema for creating an employee."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=50)
    salary: float = Field(..., gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "salary": 75000.00,
            }
        }
    }


class EmployeeUpdate(BaseModel):
    """Request schema for updating employee fields."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    salary: Optional[float] = Field(None, gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {"salary": 80000.00}
        }
    }


class TextFileCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content: str
    directory: str = Field(default="uploads", pattern="^(uploads|reports)$")


class TextFileAppend(BaseModel):
    content: str = Field(..., min_length=1)


class RenameFileRequest(BaseModel):
    new_filename: str = Field(..., min_length=1, max_length=255)


class CopyFileRequest(BaseModel):
    new_name: str = Field(..., min_length=1, max_length=255)


class CSVWriteRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    data: list[dict]
    directory: str = Field(default="reports", pattern="^(uploads|reports)$")


class JSONWriteRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    data: Any
    directory: str = Field(default="reports", pattern="^(uploads|reports)$")


# ============================================================
# SHARED ERROR MAPPING
# ============================================================

def raise_file_http_error(error: str) -> None:
    """Convert file-operation errors into suitable HTTP responses."""
    message = error or "File operation failed"
    normalized = message.lower()

    if "already exists" in normalized:
        raise HTTPException(status_code=409, detail=message)

    if "not found" in normalized:
        raise HTTPException(status_code=404, detail=message)

    if (
        "invalid filename" in normalized
        or "invalid file path" in normalized
        or "directory paths" in normalized
        or "directory must be" in normalized
        or "non-empty string" in normalized
    ):
        raise HTTPException(status_code=400, detail=message)

    if "permission denied" in normalized:
        raise HTTPException(status_code=403, detail=message)

    raise HTTPException(status_code=400, detail=message)


def checked_file_result(result: dict) -> dict:
    """Return successful helper results or raise an HTTP error."""
    if not result.get("success", False):
        raise_file_http_error(result.get("error", "File operation failed"))
    return result


def validate_filename(filename: str) -> None:
    """Reject paths instead of accepting directory components."""
    if (
        not filename
        or not filename.strip()
        or filename in {".", ".."}
        or Path(filename).name != filename
        or "/" in filename
        or "\\" in filename
    ):
        raise HTTPException(status_code=400, detail="Invalid filename")


# ============================================================
# GENERAL ENDPOINTS
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Employee Management API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "create_employee": "POST /employees",
            "get_all_employees": "GET /employees",
            "get_employee": "GET /employees/{employee_id}",
            "update_employee": "PUT /employees/{employee_id}",
            "delete_employee": "DELETE /employees/{employee_id}",
            "search_employees": "GET /employees/search/",
            "create_text_file": "POST /files/text",
            "read_text_file": "GET /files/text/{filename}",
            "append_text_file": "POST /files/text/{filename}/append",
            "check_file_exists": "GET /files/exists/{filename}",
            "rename_file": "PUT /files/rename/{filename}",
            "copy_file": "POST /files/copy/{filename}",
            "delete_file": "DELETE /files/{filename}",
            "write_csv": "POST /files/csv",
            "read_csv": "GET /files/csv/{filename}",
            "write_json": "POST /files/json",
            "read_json": "GET /files/json/{filename}",
            "upload": "POST /files/upload",
            "download": "GET /files/download/{filename}",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Employee Management API"}


# ============================================================
# EMPLOYEE CRUD
# ============================================================

@app.post("/employees", status_code=201)
def create_employee(employee: EmployeeCreate):
    result = employee_queries.create_employee(
        name=employee.name,
        email=str(employee.email),
        department=employee.department,
        salary=employee.salary,
    )

    if result.get("success"):
        return {
            "message": result["message"],
            "employee_id": result["id"],
        }

    error = result.get("error", "Unable to create employee")

    if "already exists" in error.lower():
        raise HTTPException(status_code=409, detail=error)

    raise HTTPException(status_code=500, detail="Unable to create employee")


@app.get("/employees")
def get_all_employees():
    result = employee_queries.get_all_employees()

    if result.get("success"):
        return {
            "count": result["count"],
            "employees": result["employees"],
        }

    raise HTTPException(status_code=500, detail="Unable to retrieve employees")


@app.get("/employees/search/")
def search_employees(
    term: str = Query(..., min_length=1, description="Search term"),
    field: str = Query(
        "name",
        pattern="^(name|department)$",
        description="Field to search",
    ),
):
    result = employee_queries.search_employees(term, field)

    if result.get("success"):
        return {
            "search_term": result["search_term"],
            "search_by": result["search_by"],
            "count": result["count"],
            "employees": result["employees"],
        }

    raise HTTPException(status_code=500, detail="Unable to search employees")


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    result = employee_queries.get_employee_by_id(employee_id)

    if result.get("success"):
        return result["employee"]

    raise HTTPException(status_code=404, detail="Employee not found")


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: EmployeeUpdate):
    result = employee_queries.update_employee(
        employee_id=employee_id,
        name=employee.name,
        email=str(employee.email) if employee.email is not None else None,
        department=employee.department,
        salary=employee.salary,
    )

    if result.get("success"):
        return {"message": result["message"]}

    error = result.get("error", "Unable to update employee")

    if "not found" in error.lower():
        raise HTTPException(status_code=404, detail=error)

    if "already exists" in error.lower():
        raise HTTPException(status_code=409, detail=error)

    raise HTTPException(status_code=500, detail="Unable to update employee")


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    result = employee_queries.delete_employee(employee_id)

    if result.get("success"):
        return {"message": result["message"]}

    error = result.get("error", "Unable to delete employee")

    if "not found" in error.lower():
        raise HTTPException(status_code=404, detail=error)

    raise HTTPException(status_code=500, detail="Unable to delete employee")


# ============================================================
# TEXT FILE OPERATIONS
# ============================================================

@app.post("/files/text", status_code=201, tags=["File Operations"])
def create_text_file_api(file_data: TextFileCreate):
    result = file_operations.create_text_file(
        filename=file_data.filename,
        content=file_data.content,
        directory=file_data.directory,
    )
    return checked_file_result(result)


@app.get("/files/text/{filename}", tags=["File Operations"])
def read_text_file_api(
    filename: str,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.read_text_file(filename, directory)
    )


@app.post("/files/text/{filename}/append", tags=["File Operations"])
def append_text_file_api(
    filename: str,
    file_data: TextFileAppend,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.append_text_file(
            filename, file_data.content, directory
        )
    )


@app.get("/files/exists/{filename}", tags=["File Operations"])
def check_file_exists_api(
    filename: str,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.check_file_exists(filename, directory)
    )


@app.put("/files/rename/{filename}", tags=["File Operations"])
def rename_file_api(
    filename: str,
    request: RenameFileRequest,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.rename_file(
            filename, request.new_filename, directory
        )
    )


@app.post("/files/copy/{filename}", tags=["File Operations"])
def copy_file_api(
    filename: str,
    request: CopyFileRequest,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.copy_file(
            filename, request.new_name, directory
        )
    )


@app.delete("/files/{filename}", tags=["File Operations"])
def delete_text_file_api(
    filename: str,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.delete_file(filename, directory)
    )


# ============================================================
# CSV AND JSON
# ============================================================

@app.post("/files/csv", status_code=201, tags=["File Operations"])
def write_csv_api(request: CSVWriteRequest):
    result = file_operations.write_csv_file(
        filename=request.filename,
        data=request.data,
        directory=request.directory,
    )
    return checked_file_result(result)


@app.get("/files/csv/{filename}", tags=["File Operations"])
def read_csv_api(
    filename: str,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.read_csv_file(filename, directory)
    )


@app.post("/files/json", status_code=201, tags=["File Operations"])
def write_json_api(request: JSONWriteRequest):
    result = file_operations.write_json_file(
        filename=request.filename,
        data=request.data,
        directory=request.directory,
    )
    return checked_file_result(result)


@app.get("/files/json/{filename}", tags=["File Operations"])
def read_json_api(
    filename: str,
    directory: str = Query("uploads", pattern="^(uploads|reports)$"),
):
    return checked_file_result(
        file_operations.read_json_file(filename, directory)
    )


# ============================================================
# FILE UPLOAD AND DOWNLOAD
# ============================================================

@app.post("/files/upload", status_code=201, tags=["File Operations"])
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename

    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    validate_filename(filename)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / filename
    size = 0

    try:
        # Exclusive mode avoids replacing existing files.
        with destination.open("xb") as output:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 5 MB limit",
                    )

                output.write(chunk)

    except FileExistsError:
        raise HTTPException(status_code=409, detail="File already exists")

    except HTTPException:
        destination.unlink(missing_ok=True)
        raise

    except OSError:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Upload failed")

    finally:
        await file.close()

    return {
        "success": True,
        "filename": filename,
        "size_bytes": size,
        "message": "File uploaded successfully",
    }


@app.get("/files/download/{filename}", tags=["File Operations"])
def download_file(filename: str):
    validate_filename(filename)

    try:
        file_path = (UPLOAD_DIR / filename).resolve()
        file_path.relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


# ============================================================
# APPLICATION STARTUP
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
