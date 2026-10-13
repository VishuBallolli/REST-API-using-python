# main.py
# This is the entry point of our FastAPI application.
# It defines all API endpoints and connects to the database and file operations.

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

import employee_queries
import file_operations

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

    name: str = Field(..., min_length=1, max_length=100, description="Employee name")
    email: EmailStr = Field(..., description="Employee email (must be valid)")
    department: str = Field(..., min_length=1, max_length=50, description="Department name")
    salary: float = Field(..., gt=0, description="Employee salary (must be positive)")

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
    """Request schema for updating one or more employee fields."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    salary: Optional[float] = Field(None, gt=0)

    model_config = {
        "json_schema_extra": {"example": {"salary": 80000.00}}
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


# ============================================================
# GENERAL API ENDPOINTS
# ============================================================

@app.get("/")
def read_root():
    """Return a welcome message and useful endpoint paths."""
    return {
        "message": "Welcome to Employee Management API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "create_employee": "POST /employees",
            "get_all_employees": "GET /employees",
            "get_employee": "GET /employees/{id}",
            "update_employee": "PUT /employees/{id}",
            "delete_employee": "DELETE /employees/{id}",
            "search_employees": "GET /employees/search",
            "create_text_file": "POST /files/text",
            "read_text_file": "GET /files/text/{filename}",
            "append_text_file": "POST /files/text/{filename}/append",
            "check_file_exists": "GET /files/exists/{filename}",
            "rename_file": "PUT /files/rename/{filename}",
            "copy_file": "POST /files/copy/{filename}",
        },
    }


@app.get("/health")
def health_check():
    """Verify that the API is running."""
    return {"status": "healthy", "service": "Employee Management API"}


# ============================================================
# EMPLOYEE CRUD ENDPOINTS
# ============================================================

@app.post("/employees", status_code=201)
def create_employee(employee: EmployeeCreate):
    """Create a new employee record."""
    result = employee_queries.create_employee(
        name=employee.name,
        email=str(employee.email),
        department=employee.department,
        salary=employee.salary,
    )

    if result["success"]:
        return {"message": result["message"], "employee_id": result["id"]}

    error = result.get("error", "Unable to create employee")
    if "already exists" in error.lower():
        raise HTTPException(status_code=409, detail=error)
    raise HTTPException(status_code=500, detail=error)


@app.get("/employees")
def get_all_employees():
    """Retrieve all employees."""
    result = employee_queries.get_all_employees()
    if result["success"]:
        return {"count": result["count"], "employees": result["employees"]}
    raise HTTPException(status_code=500, detail=result.get("error", "Unable to retrieve employees"))


@app.get("/employees/search/")
def search_employees(
    term: str = Query(..., min_length=1, description="Search term"),
    field: str = Query("name", pattern="^(name|department)$", description="Field to search (name or department)"),
):
    """Search employees by partial name or department match."""
    result = employee_queries.search_employees(term, field)
    if result["success"]:
        return {
            "search_term": result["search_term"],
            "search_by": result["search_by"],
            "count": result["count"],
            "employees": result["employees"],
        }
    raise HTTPException(status_code=500, detail=result.get("error", "Unable to search employees"))


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    """Retrieve one employee by ID."""
    result = employee_queries.get_employee_by_id(employee_id)
    if result["success"]:
        return result["employee"]
    raise HTTPException(status_code=404, detail=result.get("error", "Employee not found"))


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: EmployeeUpdate):
    """Update provided fields for an employee."""
    result = employee_queries.update_employee(
        employee_id=employee_id,
        name=employee.name,
        email=str(employee.email) if employee.email is not None else None,
        department=employee.department,
        salary=employee.salary,
    )
    if result["success"]:
        return {"message": result["message"]}

    error = result.get("error", "Unable to update employee")
    if "not found" in error.lower():
        raise HTTPException(status_code=404, detail=error)
    if "already exists" in error.lower():
        raise HTTPException(status_code=409, detail=error)
    raise HTTPException(status_code=500, detail=error)


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    """Delete an employee by ID."""
    result = employee_queries.delete_employee(employee_id)
    if result["success"]:
        return {"message": result["message"]}

    error = result.get("error", "Unable to delete employee")
    if "not found" in error.lower():
        raise HTTPException(status_code=404, detail=error)
    raise HTTPException(status_code=500, detail=error)


# ============================================================
# FILE OPERATION ENDPOINTS
# The helper functions themselves remain in file_operations.py.
# ============================================================

@app.post("/files/text", status_code=201, tags=["File Operations"])
def create_text_file_api(file_data: TextFileCreate):
    """Create a text file in the uploads or reports directory."""
    result = file_operations.create_text_file(
        filename=file_data.filename,
        content=file_data.content,
        directory=file_data.directory,
    )
    if not result["success"]:
        error = result.get("error", "Unable to create file")
        if "already exists" in error.lower():
            raise HTTPException(status_code=409, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return result


@app.get("/files/text/{filename}", tags=["File Operations"])
def read_text_file_api(
    filename: str,
    directory: str = Query(default="uploads", pattern="^(uploads|reports)$"),
):
    """Read the contents of an existing text file."""
    result = file_operations.read_text_file(filename=filename, directory=directory)
    if not result["success"]:
        error = result.get("error", "Unable to read file")
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return result


@app.post("/files/text/{filename}/append", tags=["File Operations"])
def append_text_file_api(
    filename: str,
    file_data: TextFileAppend,
    directory: str = Query(default="uploads", pattern="^(uploads|reports)$"),
):
    """Append text to an existing text file."""
    result = file_operations.append_text_file(
        filename=filename,
        content=file_data.content,
        directory=directory,
    )
    if not result["success"]:
        error = result.get("error", "Unable to append to file")
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return result


@app.get("/files/exists/{filename}", tags=["File Operations"])
def check_file_exists_api(
    filename: str,
    directory: str = Query(default="uploads", pattern="^(uploads|reports)$"),
):
    """Check whether a file exists."""
    result = file_operations.check_file_exists(filename=filename, directory=directory)
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Unable to check file"))
    return result


@app.put("/files/rename/{filename}", tags=["File Operations"])
def rename_file_api(
    filename: str,
    request: RenameFileRequest,
    directory: str = Query(default="uploads", pattern="^(uploads|reports)$"),
):
    """Rename an existing file."""
    result = file_operations.rename_file(
        old_name=filename,
        new_name=request.new_filename,
        directory=directory,
    )
    if not result["success"]:
        error = result.get("error", "Unable to rename file")
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        if "already exists" in error.lower():
            raise HTTPException(status_code=409, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return result


@app.post("/files/copy/{filename}", tags=["File Operations"])
def copy_file_api(
    filename: str,
    request: CopyFileRequest,
    directory: str = Query(default="uploads", pattern="^(uploads|reports)$"),
):
    """Copy an existing file with a new filename."""
    result = file_operations.copy_file(
        filename=filename,
        new_name=request.new_name,
        directory=directory,
    )
    if not result["success"]:
        error = result.get("error", "Unable to copy file")
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        if "already exists" in error.lower():
            raise HTTPException(status_code=409, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return result


# Run with: python -m uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
