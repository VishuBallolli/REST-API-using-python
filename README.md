# Employee Management REST API

A Python-based REST API built with **FastAPI and MySQL/MariaDB** for managing employee records and performing file operations.

## Project Status

**Core implementation completed; final verification and security review in progress.**

- Employee CRUD and search APIs: Implemented
- Text file operations: Implemented
- File rename, copy, and delete: Implemented
- CSV and JSON read/write APIs: Implemented and tested
- File upload and download: Implemented and tested
- GitHub version control: Changes committed and pushed

## Technologies Used

- Python 3.13
- FastAPI
- Uvicorn
- MySQL / MariaDB
- `mysql-connector-python`
- `python-dotenv`
- Pydantic
- `python-multipart`
- Swagger UI
- Postman

## Project Structure

```text
REST-API-using-python/
├── main.py
├── database.py
├── employee_queries.py
├── file_operations.py
├── requirements.txt
├── setup_database.sql
├── .env.example
├── .gitignore
├── STAGE_2_GUIDE.md
├── STAGE_3_GUIDE.md
├── STAGE_4_GUIDE.md
├── uploads/
├── reports/
└── README.md
```

## Prerequisites

- Python 3.10 or later
- MySQL or MariaDB
- Git
- VS Code (recommended)
- Postman (optional)

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/VishuBallolli/REST-API-using-python.git
cd REST-API-using-python
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and configure your local database settings.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=employee_db
DB_PORT=3306

API_HOST=127.0.0.1
API_PORT=8000

MAX_UPLOAD_SIZE_MB=5
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
```

Use the variable names expected by your actual application configuration. Never commit real database credentials or your `.env` file to GitHub.

### 5. Initialize the database

Start MySQL/MariaDB. If you use XAMPP, start MySQL from the XAMPP Control Panel.

Follow `setup_database.sql` to create the required database and tables. Run `python database.py` only if that file supports database initialization in your current implementation.

Ensure your `.env` settings match your database configuration.

### 6. Start the API server

```bash
python -m uvicorn main:app --reload
```

### 7. Open the API documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## API Features

### Employee Management

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/employees` | Create an employee |
| GET | `/employees` | Retrieve all employees |
| GET | `/employees/{employee_id}` | Retrieve one employee |
| PUT | `/employees/{employee_id}` | Update an employee |
| DELETE | `/employees/{employee_id}` | Delete an employee |
| GET | `/employees/search/?term=Rahul&field=name` | Search by name or department |

### Text File Operations

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/files/text` | Create a text file |
| GET | `/files/text/{filename}` | Read a text file |
| POST | `/files/text/{filename}/append` | Append content |
| GET | `/files/exists/{filename}` | Check whether a file exists |
| PUT | `/files/rename/{filename}` | Rename a file |
| POST | `/files/copy/{filename}` | Copy a file |
| DELETE | `/files/{filename}` | Delete a file |

For text-file operations that accept a `directory` query parameter, the supported directories are `uploads` and `reports`.

### CSV and JSON Operations

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/files/csv` | Write CSV data |
| GET | `/files/csv/{filename}` | Read CSV data |
| POST | `/files/json` | Write JSON data |
| GET | `/files/json/{filename}` | Read JSON data |

The write endpoints accept a filename, data, and a destination directory. Read endpoints accept a filename and optional directory.

### File Upload and Download

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/files/upload` | Upload a file |
| GET | `/files/download/{filename}` | Download an uploaded file |

The upload endpoint accepts multipart form data and enforces a 5 MB limit in the current implementation. Existing filenames are not overwritten.

## Testing

Use Swagger UI at `/docs` to explore and test endpoints.

Verified during development:

- CSV creation and reading
- JSON creation and reading
- File upload and download
- Duplicate upload rejection
- Missing-file handling
- Employee and text-file operations tested during development

Run additional regression tests before deployment, including database failures, invalid inputs, and file-path security cases.

## Security Considerations

- Keep `.env` and real credentials out of version control.
- Validate request data and file paths.
- Enforce file size limits.
- Test unauthorized or invalid requests and error handling.
- Use appropriate authentication and authorization before exposing the API publicly.
- Review file overwrite behavior and database error handling before production deployment.

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Documentation](https://docs.python.org/3/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Postman Learning Center](https://learning.postman.com/)

## Author

Developed as a hands-on learning project to practice Python backend development, REST APIs, database integration, and file handling.

**Organization:** Nighan2 Lab Pvt. Ltd.
