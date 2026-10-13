# Stage 2: Install Packages and Create First API

## 📚 Learning Objectives

By the end of this stage, you will understand:
- How to install Python packages using pip
- What each package does in our project
- How FastAPI works at a basic level
- How to create API endpoints
- How to run and test a FastAPI application

---

## 🎯 Problem Statement

Now that our environment is set up, we need to:
1. Install all required Python packages
2. Understand what each package does
3. Create a simple "Hello World" API
4. Run the API server
5. Test the API using a browser and Postman

---

## 📦 Understanding Python Packages

### What is pip?

**pip** is Python's package installer. Think of it like an app store for Python code.

```powershell
pip install fastapi    # Downloads and installs FastAPI
pip list              # Shows all installed packages
pip uninstall fastapi # Removes a package
```

### Packages We're Installing

Let's understand each package in `requirements.txt`:

#### 1. **FastAPI** (fastapi==0.104.1)
- **What it is**: Modern web framework for building APIs
- **Why we need it**: To create REST API endpoints easily
- **Alternative**: Flask (older, simpler but less features)

**Example:**
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Hello World"}
```

#### 2. **Uvicorn** (uvicorn==0.24.0)
- **What it is**: ASGI server (web server)
- **Why we need it**: FastAPI needs a server to run
- **Think of it as**: The engine that powers your API

**Analogy**:
- FastAPI = Your car (the application)
- Uvicorn = The engine that makes it run

#### 3. **MySQL Connector** (mysql-connector-python==8.2.0)
- **What it is**: Official MySQL driver for Python
- **Why we need it**: To connect Python to MySQL database
- **Alternative**: PyMySQL, SQLAlchemy

**Example:**
```python
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="employee_db"
)
```

#### 4. **Python-dotenv** (python-dotenv==1.0.0)
- **What it is**: Loads environment variables from .env file
- **Why we need it**: To read database credentials securely

**Example:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Reads .env file
password = os.getenv("DB_PASSWORD")  # Gets DB_PASSWORD value
```

#### 5. **Python-multipart** (python-multipart==0.0.6)
- **What it is**: Handles file uploads in FastAPI
- **Why we need it**: To accept file uploads from users
- **When used**: File upload endpoints

#### 6. **Pydantic** (pydantic==2.5.0)
- **What it is**: Data validation using Python type hints
- **Why we need it**: Automatically validates API input
- **Comes with**: FastAPI (included automatically)

**Example:**
```python
from pydantic import BaseModel

class Employee(BaseModel):
    name: str
    email: str
    salary: float

# If user sends salary as text, Pydantic rejects it automatically
```

---

## 🛠️ Step-by-Step Instructions

### Step 1: Verify Virtual Environment is Active

**Check your terminal prompt:**
```powershell
(venv) PS C:\REST-API-using-python>
```

You should see `(venv)` at the beginning.

**If NOT active, activate it:**
```powershell
.\venv\Scripts\Activate.ps1
```

---

### Step 2: Upgrade pip (Optional but Recommended)

```powershell
python -m pip install --upgrade pip
```

**What this does:** Updates pip to the latest version for better compatibility.

**Expected output:**
```
Successfully installed pip-23.x.x
```

---

### Step 3: Install All Packages

```powershell
pip install -r requirements.txt
```

**What this does:** Reads `requirements.txt` and installs all listed packages.

**Expected output:**
```
Collecting fastapi==0.104.1
  Downloading fastapi-0.104.1-py3-none-any.whl
Collecting uvicorn==0.24.0
  Downloading uvicorn-0.24.0-py3-none-any.whl
...
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**This takes:** 30-60 seconds depending on your internet speed.

---

### Step 4: Verify Installation

**Check installed packages:**
```powershell
pip list
```

**Expected output:**
```
Package                Version
---------------------- -------
fastapi               0.104.1
uvicorn               0.24.0
mysql-connector-python 8.2.0
python-dotenv         1.0.0
python-multipart      0.0.6
pydantic              2.5.0
...
```

**Verify specific package:**
```powershell
pip show fastapi
```

**Expected output:**
```
Name: fastapi
Version: 0.104.1
Summary: FastAPI framework, high performance, easy to learn...
```

---

### Step 5: Understanding main.py

Let's break down the `main.py` file line by line:

```python
from fastapi import FastAPI
```
- **Imports** the FastAPI class
- Like importing a tool from a toolbox

```python
app = FastAPI(
    title="Employee Management API",
    description="A REST API for managing employee records",
    version="1.0.0"
)
```
- **Creates** a FastAPI application instance
- `app` is now your API application
- The parameters show up in the auto-generated documentation

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to Employee Management API"}
```
- `@app.get("/")` is a **decorator** that creates a GET endpoint at the root URL
- When someone visits `http://localhost:8000/`, this function runs
- Returns a **dictionary** which FastAPI converts to JSON automatically

**What's a decorator?**
- A decorator is a special function that modifies another function
- `@app.get("/")` tells FastAPI: "When someone makes a GET request to /, run this function"

**Why return a dictionary?**
- FastAPI automatically converts Python dictionaries to JSON
- JSON is the standard format for REST APIs

---

### Step 6: Run the API Server

**Method 1: Using Uvicorn Command (Recommended)**

```powershell
uvicorn main:app --reload
```

**Understanding the command:**
- `uvicorn` - The server program
- `main:app` - Run the `app` object from `main.py` file
- `--reload` - Auto-restart when code changes (for development)

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**What this means:**
- ✅ Server is running successfully
- ✅ Your API is accessible at `http://127.0.0.1:8000`
- ✅ Auto-reload is enabled

**Method 2: Using Python (Alternative)**

```powershell
python main.py
```

This uses the `if __name__ == "__main__"` block in main.py.

---

### Step 7: Test the API in Browser

**Open your browser and visit:**

1. **Root endpoint:**
   ```
   http://localhost:8000/
   ```

   **Expected response:**
   ```json
   {
     "message": "Welcome to Employee Management API",
     "status": "running",
     "version": "1.0.0"
   }
   ```

2. **Health check endpoint:**
   ```
   http://localhost:8000/health
   ```

   **Expected response:**
   ```json
   {
     "status": "healthy",
     "service": "Employee Management API"
   }
   ```

3. **Interactive API documentation (Swagger UI):**
   ```
   http://localhost:8000/docs
   ```

   **What you'll see:**
   - Beautiful interactive documentation
   - Automatically generated by FastAPI
   - You can test endpoints directly here!

4. **Alternative API documentation (ReDoc):**
   ```
   http://localhost:8000/redoc
   ```

   **What you'll see:**
   - Different documentation style
   - Also automatically generated

---

### Step 8: Test with Postman

#### Install Postman (if not already installed)
- Download from: https://www.postman.com/downloads/
- Install and open Postman

#### Test the Root Endpoint

1. **Create a new request:**
   - Click "New" > "HTTP Request"

2. **Configure the request:**
   - Method: `GET`
   - URL: `http://localhost:8000/`

3. **Send the request:**
   - Click "Send"

4. **Expected response:**
   ```json
   {
     "message": "Welcome to Employee Management API",
     "status": "running",
     "version": "1.0.0"
   }
   ```
   - Status: `200 OK`
   - Response time: ~10-50ms

#### Test the Health Check Endpoint

1. **Configure the request:**
   - Method: `GET`
   - URL: `http://localhost:8000/health`

2. **Send and verify response**

---

## 📊 How FastAPI Works (Simplified)

```
1. User makes request → http://localhost:8000/

2. Uvicorn (server) receives the request

3. FastAPI checks which function handles "/"
   → Finds @app.get("/") decorator

4. Runs the read_root() function

5. Function returns {"message": "Welcome..."}

6. FastAPI converts dictionary to JSON

7. Uvicorn sends JSON response back to user
```

---

## 🎓 Interview Questions with Answers

### Question 1: What is FastAPI and why would you use it?

**Answer:**
FastAPI is a modern, fast (high-performance) web framework for building APIs with Python based on standard Python type hints.

**Key features:**
- **Fast**: High performance, on par with NodeJS and Go
- **Easy**: Intuitive to learn and use
- **Automatic docs**: Generates interactive API documentation automatically
- **Type safety**: Uses Python type hints for validation
- **Modern**: Based on modern Python features (async/await)

**Why use it:**
- Faster development than Flask or Django
- Automatic data validation
- Built-in documentation
- Great for REST APIs and microservices

**Example use cases:**
- REST APIs
- Microservices
- Backend for mobile apps
- Real-time data APIs

---

### Question 2: What is the difference between FastAPI and Flask?

**Answer:**

| Feature | FastAPI | Flask |
|---------|---------|-------|
| **Performance** | Very fast (async support) | Moderate (synchronous) |
| **Documentation** | Auto-generated (Swagger) | Manual |
| **Data validation** | Built-in (Pydantic) | Requires extensions |
| **Type hints** | Required & enforced | Optional |
| **Learning curve** | Moderate | Easy |
| **Best for** | Modern APIs | Simple web apps |

**When to use FastAPI:**
- Building new REST APIs
- Need high performance
- Want automatic documentation
- Working with modern Python (3.7+)

**When to use Flask:**
- Simple web applications
- Need more flexibility
- Team familiar with Flask
- Smaller projects

---

### Question 3: What is Uvicorn and why do we need it?

**Answer:**
Uvicorn is an ASGI (Asynchronous Server Gateway Interface) server implementation. It's the web server that runs your FastAPI application.

**Why we need it:**
- FastAPI is a framework (defines how to write code)
- Uvicorn is a server (runs the code and handles HTTP)
- You can't run FastAPI without a server

**Analogy:**
- FastAPI = Car (the application)
- Uvicorn = Engine (makes it run)

**Command explanation:**
```powershell
uvicorn main:app --reload
```
- `main` = Python file name (main.py)
- `app` = FastAPI instance variable name
- `--reload` = Auto-restart on code changes (dev mode)

**Alternatives:**
- Gunicorn (production-ready, UNIX only)
- Hypercorn (supports HTTP/2)
- Daphne (Django channels server)

---

### Question 4: What are decorators in Python? How does @app.get() work?

**Answer:**
A decorator is a function that modifies the behavior of another function. In FastAPI, decorators register functions as endpoint handlers.

**Simple example:**
```python
@app.get("/hello")
def say_hello():
    return {"message": "Hello"}
```

**What happens:**
1. `@app.get("/hello")` is the decorator
2. It tells FastAPI: "When a GET request comes to /hello, run say_hello()"
3. FastAPI registers this mapping internally
4. When request arrives, FastAPI calls the function

**Without decorator (equivalent):**
```python
def say_hello():
    return {"message": "Hello"}

app.add_api_route("/hello", say_hello, methods=["GET"])
```

**Common decorators:**
- `@app.get()` - Handle GET requests
- `@app.post()` - Handle POST requests
- `@app.put()` - Handle PUT requests
- `@app.delete()` - Handle DELETE requests

---

### Question 5: What is the purpose of `if __name__ == "__main__":` in Python?

**Answer:**
This block runs only when the file is executed directly, not when it's imported as a module.

**Scenario 1: Run directly**
```powershell
python main.py
```
- `__name__` equals `"__main__"`
- Code inside the block runs

**Scenario 2: Import in another file**
```python
from main import app
```
- `__name__` equals `"main"` (file name)
- Code inside the block doesn't run

**Why it's useful:**
```python
if __name__ == "__main__":
    # This code only runs during testing/development
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

**In production:**
- You use: `uvicorn main:app`
- The if block is ignored
- More control over server settings

**Best practice:**
- Use for testing/development runs
- Use uvicorn command for production

---

## 💪 Practice Tasks

### Task 1: Create a New Endpoint

**Instructions:**
Add a new endpoint `/about` that returns:
```json
{
  "project": "Employee Management API",
  "author": "Your Name",
  "technologies": ["Python", "FastAPI", "MySQL"]
}
```

**Solution:**
```python
@app.get("/about")
def about_api():
    """
    About endpoint - returns project information
    """
    return {
        "project": "Employee Management API",
        "author": "Your Name",
        "technologies": ["Python", "FastAPI", "MySQL"]
    }
```

**Test it:**
1. Add the code to main.py
2. The server will auto-reload (if --reload is enabled)
3. Visit: http://localhost:8000/about
4. You should see your JSON response

---

### Task 2: Create a Greeting Endpoint with Parameter

**Instructions:**
Create an endpoint `/greet/{name}` that returns a personalized greeting.

**Example:**
- Visit: `http://localhost:8000/greet/John`
- Response: `{"message": "Hello, John! Welcome to our API"}`

**Solution:**
```python
@app.get("/greet/{name}")
def greet_user(name: str):
    """
    Greet endpoint - returns personalized greeting

    Args:
        name (str): User's name from URL path

    Returns:
        dict: Greeting message
    """
    return {
        "message": f"Hello, {name}! Welcome to our API"
    }
```

**Understanding:**
- `{name}` in the path is a **path parameter**
- FastAPI automatically extracts it from the URL
- The `name: str` parameter receives the value
- `f"Hello, {name}!"` is an f-string (formatted string)

**Test with different names:**
- http://localhost:8000/greet/Alice
- http://localhost:8000/greet/Bob
- http://localhost:8000/greet/Charlie

---

## ✅ Verification Checklist

Before moving to Stage 3, verify:

- [ ] All packages installed successfully (`pip list` shows them)
- [ ] `main.py` file created
- [ ] API server runs without errors
- [ ] Browser shows JSON at http://localhost:8000/
- [ ] Health check endpoint works
- [ ] Swagger docs accessible at http://localhost:8000/docs
- [ ] Postman can make successful requests
- [ ] Both practice tasks completed and working

---

## 🐛 Common Issues and Solutions

### Issue 1: "uvicorn: command not found"

**Cause:** Virtual environment not activated or uvicorn not installed

**Solution:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall uvicorn
pip install uvicorn
```

---

### Issue 2: "Port 8000 already in use"

**Cause:** Another application is using port 8000

**Solution 1: Use a different port**
```powershell
uvicorn main:app --reload --port 8001
```

**Solution 2: Kill the process using port 8000**
```powershell
# Find the process
netstat -ano | findstr :8000

# Kill it (replace PID with actual process ID)
taskkill /PID <PID> /F
```

---

### Issue 3: "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** Package not installed or wrong Python environment

**Solution:**
```powershell
# Verify virtual environment is active (should see (venv))
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Verify installation
pip show fastapi
```

---

### Issue 4: Changes not reflecting in browser

**Cause:** Browser cache or server not reloading

**Solution:**
1. **Hard refresh browser:** Ctrl + Shift + R (Windows)
2. **Restart server with --reload:**
   ```powershell
   uvicorn main:app --reload
   ```
3. **Clear browser cache**

---

### Issue 5: "import error" or "cannot import name"

**Cause:** Typo in import statement or wrong file name

**Solution:**
```python
# Correct imports
from fastapi import FastAPI  # Capital F, capital A

# Check file name matches
# If file is "main.py", use: uvicorn main:app
# If file is "app.py", use: uvicorn app:app
```

---

## 📚 Key Takeaways

### What You Learned

1. **Package Management:**
   - Installing packages with pip
   - Understanding requirements.txt
   - Each package's purpose

2. **FastAPI Basics:**
   - Creating a FastAPI app
   - Defining endpoints with decorators
   - Automatic JSON conversion

3. **Running the Server:**
   - Using uvicorn command
   - Auto-reload for development
   - Accessing the API

4. **Testing:**
   - Browser testing
   - Postman testing
   - Auto-generated documentation

5. **Python Concepts:**
   - Decorators
   - if __name__ == "__main__"
   - F-strings
   - Type hints

---

## 🚀 Next Steps - Stage 3

In Stage 3, we will:
- ✅ Install and configure MySQL
- ✅ Create the employee database
- ✅ Create the employees table
- ✅ Understand SQL and database concepts
- ✅ Learn about primary keys, constraints, and data types

**Prerequisites for Stage 3:**
- MySQL Server installed
- MySQL credentials ready
- Stage 2 completed and verified

---

## 📚 Additional Resources

- FastAPI Official Tutorial: https://fastapi.tiangolo.com/tutorial/
- Uvicorn Documentation: https://www.uvicorn.org/
- Python Decorators: https://realpython.com/primer-on-python-decorators/
- HTTP Methods: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
- REST API Design: https://restfulapi.net/

---

**🎉 Congratulations!** You've successfully created your first FastAPI application!

**When you're ready, let me know and we'll move to Stage 3** where we'll set up MySQL and create our employee database! 🚀
