# Employee Management REST API

A Python-based REST API built with **FastAPI and MySQL** for managing employee records and performing file operations.

## Project Status

🚧 **Development in Progress**

- Employee CRUD and search APIs: Implemented and tested
- Text file operations: Implemented and tested
- File rename and copy: Implemented and tested
- CSV and JSON operations: Remaining
- File upload and download: Remaining
- Final security review and testing: Remaining

## Technologies Used

- Python 3.13
- FastAPI
- Uvicorn
- MySQL / MariaDB
- `mysql-connector-python`
- `python-dotenv`
- Pydantic
- Postman and Swagger UI

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
- MySQL or MariaDB running locally
- Git
- VS Code (recommended)
- Postman (for API testing)

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/VishuBallolli/REST-API-using-python.git
cd REST-API-using-python
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the database settings.

Example configuration:

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

**Security:** Never commit your real `.env` file or database credentials to GitHub.

### 5. Initialize the database

Start your MySQL/MariaDB service. If using XAMPP, start MySQL from the XAMPP Control Panel.

Follow the instructions in `setup_database.sql` or use the project's database initialization script:

```bash
python database.py
```

Ensure the database connection settings in `.env` are correct before running the script.

### 6. Start the API server

```bash
python -m uvicorn main:app --reload
```

### 7. Open the API documentation

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Implemented Features

### Employee Management

- Create employee records
- Retrieve employee records
- Update employee records
- Delete employee records
- Search employees

### File Operations

- Create text files
- Read text file contents
- Append text to files
- Check file existence
- Rename files
- Copy files

These operations have been tested using Swagger UI during development.

## Remaining Work

- [ ] Complete remaining file APIs, including deletion
- [ ] Test CSV import/export operations
- [ ] Test JSON import/export operations
- [ ] Implement and test file uploads and downloads
- [ ] Review validation and error handling
- [ ] Review file-path security and upload restrictions
- [ ] Test endpoints and edge cases using Postman
- [ ] Complete final documentation and verification

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Documentation](https://docs.python.org/3/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Postman Learning Center](https://learning.postman.com/)

## Author

Developed as a hands-on learning project to practice Python backend development, REST APIs, database integration, and file handling.

**Organization:** Nighan2 Lab Pvt. Ltd.