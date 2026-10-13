# Stage 4: Employee CRUD Operations and API Integration

## 📚 Learning Objectives

By the end of this stage, you will understand:
- CRUD operations (Create, Read, Update, Delete)
- SQL queries for each operation
- Parameterized queries and SQL injection prevention
- Pydantic models for data validation
- HTTP status codes and error handling
- FastAPI endpoint design patterns

---

## 🎯 Problem Statement

We need to create a complete set of APIs to manage employees:
1. **Create** - Add new employees to database
2. **Read** - Get all employees or specific employee
3. **Update** - Modify employee information
4. **Delete** - Remove employees
5. **Search** - Find employees by name or department

Each operation needs proper error handling and validation.

---

## 📖 Core Concepts Explained

### 1. CRUD Operations

**CRUD** is an acronym for the four basic database operations:

| Operation | SQL Command | HTTP Method | Purpose |
|-----------|-------------|-------------|---------|
| **Create** | INSERT | POST | Add new record |
| **Read** | SELECT | GET | Retrieve records |
| **Update** | UPDATE | PUT/PATCH | Modify existing record |
| **Delete** | DELETE | DELETE | Remove record |

**Real-world analogy:**
- **Create** = Adding a contact to your phone
- **Read** = Viewing contact details
- **Update** = Changing someone's phone number
- **Delete** = Removing a contact

### 2. SQL Injection and Prevention

**What is SQL Injection?**

A security vulnerability where attackers inject malicious SQL code.

**Vulnerable code (NEVER DO THIS!):**
```python
# BAD - Using f-strings for SQL queries
employee_id = "1; DROP TABLE employees; --"
query = f"SELECT * FROM employees WHERE id = {employee_id}"
# This executes: SELECT * FROM employees WHERE id = 1; DROP TABLE employees; --
# Your entire table gets deleted!
```

**Safe code (ALWAYS DO THIS):**
```python
# GOOD - Using parameterized queries
employee_id = "1; DROP TABLE employees; --"
query = "SELECT * FROM employees WHERE id = %s"
cursor.execute(query, (employee_id,))
# mysql-connector automatically escapes the value
# It's treated as data, not SQL code
```

**Why parameterized queries are safe:**
- Values are automatically escaped
- Treated as data, not SQL commands
- Database driver handles security
- No way to inject malicious code

**Key rule: NEVER use f-strings or string concatenation for SQL queries!**

### 3. HTTP Status Codes

Status codes tell the client what happened:

| Code | Meaning | When to Use |
|------|---------|-------------|
| **200 OK** | Success | Successful GET, PUT, DELETE |
| **201 Created** | Resource created | Successful POST |
| **204 No Content** | Success, no data | Successful DELETE (alternative) |
| **400 Bad Request** | Invalid input | Validation failed |
| **404 Not Found** | Resource missing | Employee doesn't exist |
| **409 Conflict** | Duplicate entry | Email already exists |
| **500 Server Error** | Server problem | Database error |

**Example scenarios:**
- User creates employee → **201 Created**
- User requests invalid email format → **400 Bad Request**
- User requests employee ID 999 (doesn't exist) → **404 Not Found**
- User tries duplicate email → **409 Conflict**
- Database connection fails → **500 Internal Server Error**

### 4. Pydantic Models

**Pydantic** provides automatic data validation using Python type hints.

**Without Pydantic:**
```python
def create_employee(data):
    # Manual validation - tedious and error-prone!
    if not data.get("name"):
        return {"error": "Name is required"}
    if not data.get("email"):
        return {"error": "Email is required"}
    if "@" not in data.get("email", ""):
        return {"error": "Invalid email"}
    if data.get("salary", 0) <= 0:
        return {"error": "Salary must be positive"}
    # ... more validation code
```

**With Pydantic:**
```python
class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    salary: float = Field(gt=0)
    
# All validation happens automatically!
# If invalid, FastAPI returns 422 with detailed error
```

**Benefits:**
- Automatic validation
- Type checking
- Clear error messages
- Self-documenting code
- Reduces boilerplate

### 5. Database Cursor Modes

**Regular cursor (returns tuples):**
```python
cursor = connection.cursor()
cursor.execute("SELECT name, email FROM employees")
result = cursor.fetchone()
# result = ('John Doe', 'john@company.com')
# Access by index: result[0], result[1]
```

**Dictionary cursor (returns dictionaries):**
```python
cursor = connection.cursor(dictionary=True)
cursor.execute("SELECT name, email FROM employees")
result = cursor.fetchone()
# result = {'name': 'John Doe', 'email': 'john@company.com'}
# Access by key: result['name'], result['email']
```

**Why dictionary cursor for APIs:**
- Easier to convert to JSON
- More readable
- Field names included
- No need to remember column order

### 6. Dynamic UPDATE Queries

Sometimes you want to update only specific fields:

```python
# User wants to update only salary
update_employee(id=1, salary=80000)  # name, email, dept stay the same

# User wants to update name and department
update_employee(id=1, name="John Smith", department="Sales")
```

**Implementation:**
```python
update_fields = []
update_values = []

if name is not None:
    update_fields.append("name = %s")
    update_values.append(name)
    
if salary is not None:
    update_fields.append("salary = %s")
    update_values.append(salary)

# Builds query like: UPDATE employees SET name = %s, salary = %s WHERE id = %s
query = f"UPDATE employees SET {', '.join(update_fields)} WHERE id = %s"
```

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Understanding employee_queries.py Structure

The file contains 6 main functions:

1. **create_employee()** - INSERT new employee
2. **get_all_employees()** - SELECT all employees
3. **get_employee_by_id()** - SELECT one employee
4. **update_employee()** - UPDATE employee fields
5. **delete_employee()** - DELETE employee
6. **search_employees()** - SELECT with LIKE operator

Each function follows this pattern:
```python
def operation():
    connection = get_db_connection()
    if not connection:
        return {"success": False, "error": "Connection failed"}
    
    try:
        cursor = connection.cursor()
        cursor.execute("SQL query", params)
        connection.commit()  # For INSERT, UPDATE, DELETE
        return {"success": True, ...}
    except Error as e:
        return {"success": False, "error": str(e)}
    finally:
        if connection.is_connected():
            connection.close()
```

### Step 2: Install Email Validation Support

```powershell
pip install "pydantic[email]"
```

This adds email validation to Pydantic's EmailStr type.

### Step 3: Test Database Functions

**Test employee_queries.py directly:**

```powershell
python employee_queries.py
```

**Expected output:**
```
Testing Employee Query Functions
==================================================

1. Creating employee...
{'success': True, 'id': 1, 'message': 'Employee created successfully with ID 1'}

2. Getting all employees...
Found 1 employees

3. Searching for 'Test'...
Found 1 matches

==================================================
Testing complete!
```

### Step 4: Understanding Pydantic Models

**EmployeeCreate model:**
```python
class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    department: str = Field(..., min_length=1, max_length=50)
    salary: float = Field(..., gt=0)
```

**Field parameters explained:**
- `...` = Required field (three dots is Python ellipsis)
- `min_length=1` = At least 1 character
- `max_length=100` = No more than 100 characters
- `gt=0` = Greater than 0
- `EmailStr` = Must be valid email format

**What validation happens automatically:**
- Empty name → Error: "Field required"
- Invalid email → Error: "Invalid email format"
- Negative salary → Error: "Salary must be greater than 0"
- Name too long → Error: "String should have at most 100 characters"

**EmployeeUpdate model:**
```python
class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    salary: Optional[float] = Field(None, gt=0)
```

**Why Optional:**
- All fields are optional
- Only provided fields get updated
- `None` means "don't update this field"

### Step 5: Run the Complete API

```powershell
uvicorn main:app --reload
```

**Server starts:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Available endpoints:**
- POST `/employees` - Create employee
- GET `/employees` - Get all employees
- GET `/employees/{id}` - Get specific employee
- PUT `/employees/{id}` - Update employee
- DELETE `/employees/{id}` - Delete employee
- GET `/employees/search/?term=...&field=...` - Search employees

---

## 🧪 Testing with Postman

### Test 1: Create Employee (POST)

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/employees`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "salary": 75000.00
}
```

**Expected Response (201 Created):**
```json
{
  "message": "Employee created successfully with ID 1",
  "employee_id": 1
}
```

**Test validation - Send invalid email:**
```json
{
  "name": "Jane",
  "email": "not-an-email",
  "department": "Marketing",
  "salary": 65000
}
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

### Test 2: Get All Employees (GET)

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/employees`

**Expected Response (200 OK):**
```json
{
  "count": 1,
  "employees": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@company.com",
      "department": "Engineering",
      "salary": 75000.00,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

### Test 3: Get Employee by ID (GET)

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/employees/1`

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "salary": 75000.00,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Test not found - Request non-existent ID:**
- URL: `http://localhost:8000/employees/999`

**Expected Response (404 Not Found):**
```json
{
  "detail": "Employee with ID 999 not found"
}
```

---

### Test 4: Update Employee (PUT)

**Request:**
- Method: `PUT`
- URL: `http://localhost:8000/employees/1`
- Body (update only salary):
```json
{
  "salary": 80000.00
}
```

**Expected Response (200 OK):**
```json
{
  "message": "Employee 1 updated successfully"
}
```

**Verify the update - GET employee 1 again:**
- Salary should now be 80000.00
- Other fields unchanged

---

### Test 5: Search Employees (GET)

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/employees/search/?term=John&field=name`

**Expected Response (200 OK):**
```json
{
  "search_term": "John",
  "search_by": "name",
  "count": 1,
  "employees": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@company.com",
      "department": "Engineering",
      "salary": 80000.00,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:35:00"
    }
  ]
}
```

**Search by department:**
- URL: `http://localhost:8000/employees/search/?term=Eng&field=department`

---

### Test 6: Delete Employee (DELETE)

**Request:**
- Method: `DELETE`
- URL: `http://localhost:8000/employees/1`

**Expected Response (200 OK):**
```json
{
  "message": "Employee 1 deleted successfully"
}
```

**Verify deletion - Try to GET employee 1:**
**Expected Response (404 Not Found):**
```json
{
  "detail": "Employee with ID 1 not found"
}
```

---

## 🎓 Interview Questions with Answers

### Question 1: What is SQL injection and how do you prevent it?

**Answer:**
SQL injection is a security vulnerability where attackers insert malicious SQL code through user inputs to manipulate or damage the database.

**Example of vulnerable code:**
```python
# NEVER DO THIS!
name = request.get("name")
query = f"SELECT * FROM employees WHERE name = '{name}'"
cursor.execute(query)
```

**Attack:**
```
User inputs: ' OR '1'='1
Final query: SELECT * FROM employees WHERE name = '' OR '1'='1'
Result: Returns ALL employees (security breach!)
```

**More dangerous attack:**
```
User inputs: '; DROP TABLE employees; --
Final query: SELECT * FROM employees WHERE name = ''; DROP TABLE employees; --'
Result: Your entire table gets deleted!
```

**Prevention - Use parameterized queries:**
```python
# ALWAYS DO THIS!
name = request.get("name")
query = "SELECT * FROM employees WHERE name = %s"
cursor.execute(query, (name,))
```

**Why it's safe:**
- `%s` is a placeholder
- mysql-connector treats the value as data, not SQL code
- Special characters are automatically escaped
- No way to inject SQL commands

**Key rules:**
1. NEVER use f-strings or + for SQL queries
2. ALWAYS use parameterized queries (%s placeholders)
3. NEVER trust user input
4. Let the database driver handle escaping

---

### Question 2: What's the difference between cursor() and cursor(dictionary=True)?

**Answer:**

**Regular cursor - Returns tuples:**
```python
cursor = connection.cursor()
cursor.execute("SELECT name, email, salary FROM employees WHERE id = 1")
result = cursor.fetchone()
# result = ('John Doe', 'john@company.com', 75000.00)

# Access by index (hard to remember)
name = result[0]
email = result[1]
salary = result[2]
```

**Dictionary cursor - Returns dictionaries:**
```python
cursor = connection.cursor(dictionary=True)
cursor.execute("SELECT name, email, salary FROM employees WHERE id = 1")
result = cursor.fetchone()
# result = {
#     'name': 'John Doe',
#     'email': 'john@company.com',
#     'salary': 75000.00
# }

# Access by key (much more readable)
name = result['name']
email = result['email']
salary = result['salary']
```

**When to use each:**

**Use regular cursor:**
- Performance-critical operations (slightly faster)
- You know the column order
- Internal processing only

**Use dictionary cursor:**
- API endpoints (easier JSON conversion)
- Readability matters
- Dynamic column selection
- Column order might change

**For REST APIs, always use dictionary=True!**

---

### Question 3: Why do we need to call connection.commit()?

**Answer:**
`connection.commit()` saves changes to the database. Without it, changes are rolled back.

**What is a transaction:**
A transaction is a group of database operations that either all succeed or all fail together.

**How it works:**
```python
connection = get_db_connection()
cursor = connection.cursor()

# These changes are TEMPORARY (in memory only)
cursor.execute("INSERT INTO employees ...")
cursor.execute("UPDATE employees ...")
cursor.execute("DELETE FROM employees ...")

# Now SAVE the changes to disk
connection.commit()
```

**Without commit:**
```python
cursor.execute("INSERT INTO employees VALUES (...)")
# Don't call commit
connection.close()
# Changes are lost! Employee was NOT inserted!
```

**When to commit:**
- After INSERT queries
- After UPDATE queries
- After DELETE queries

**When NOT to commit:**
- After SELECT queries (read-only)
- After CREATE TABLE (auto-commits)
- After errors (let it rollback)

**Rollback example:**
```python
try:
    cursor.execute("INSERT INTO employees ...")
    cursor.execute("UPDATE accounts SET balance = balance - 1000 ...")
    connection.commit()  # Both succeed
except Error:
    connection.rollback()  # Both fail (atomicity)
```

**Benefits:**
- Data consistency
- Can undo changes on error
- Multiple operations as single unit
- Protects against partial updates

---

### Question 4: What is Pydantic and why use it in FastAPI?

**Answer:**
Pydantic is a data validation library that uses Python type hints to validate and parse data.

**Without Pydantic (manual validation):**
```python
@app.post("/employees")
def create_employee(data: dict):
    # Manual validation - tedious!
    if "name" not in data:
        raise HTTPException(400, "Name is required")
    if not isinstance(data["name"], str):
        raise HTTPException(400, "Name must be string")
    if len(data["name"]) > 100:
        raise HTTPException(400, "Name too long")
    if "email" not in data:
        raise HTTPException(400, "Email is required")
    if "@" not in data["email"]:
        raise HTTPException(400, "Invalid email")
    # ... 20 more lines of validation
```

**With Pydantic (automatic validation):**
```python
class Employee(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr
    salary: float = Field(gt=0)

@app.post("/employees")
def create_employee(employee: Employee):
    # All validation happens automatically!
    # If invalid, FastAPI returns 422 with detailed errors
    pass
```

**Benefits:**
1. **Automatic validation** - No manual checks needed
2. **Type safety** - Catches type errors at runtime
3. **Clear errors** - User gets detailed validation messages
4. **Self-documenting** - Code shows what fields are required
5. **Auto docs** - FastAPI uses models to generate docs
6. **Data parsing** - Converts strings to proper types

**Example validation:**
```python
class Employee(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    salary: float = Field(gt=0, le=1000000)
    department: str
```

**What Pydantic validates:**
- Name is string between 1-100 characters
- Email is valid email format
- Salary is positive and ≤ 1,000,000
- Department is provided

**Invalid input:**
```json
{"name": "", "email": "invalid", "salary": -100}
```

**Pydantic error response:**
```json
{
  "detail": [
    {"loc": ["body", "name"], "msg": "ensure this value has at least 1 characters"},
    {"loc": ["body", "email"], "msg": "value is not a valid email address"},
    {"loc": ["body", "salary"], "msg": "ensure this value is greater than 0"}
  ]
}
```

---

### Question 5: What's the difference between PUT and PATCH HTTP methods?

**Answer:**

| Aspect | PUT | PATCH |
|--------|-----|-------|
| **Purpose** | Full replacement | Partial update |
| **Fields** | All fields required | Only changed fields |
| **Idempotent** | Yes | Yes |
| **Example** | Replace entire employee | Update only salary |

**PUT - Full replacement:**
```http
PUT /employees/1
{
  "name": "John Doe",
  "email": "john@company.com",
  "department": "Engineering",
  "salary": 80000
}
```
- Must provide ALL fields
- Completely replaces the resource
- Missing fields become NULL or default

**PATCH - Partial update:**
```http
PATCH /employees/1
{
  "salary": 80000
}
```
- Provide only fields to change
- Other fields remain unchanged
- More flexible

**In our API:**
We use PUT but implement PATCH behavior (partial updates).

**Implementation:**
```python
class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    salary: Optional[float] = None
```

- All fields optional
- Only provided fields are updated
- This is actually PATCH behavior with PUT method

**Best practice:**
- Use PATCH for partial updates
- Use PUT for full replacements
- Be consistent in your API

**Our choice:** Using PUT with optional fields is common and acceptable.

---

## 💪 Practice Tasks

### Task 1: Add Employee Count Endpoint

**Goal:** Create a new endpoint that returns total number of employees.

**Requirements:**
- Endpoint: GET `/employees/count`
- Returns: `{"count": 10}`

**Solution:**

**1. Add function in employee_queries.py:**
```python
def get_employee_count():
    """
    Returns the total number of employees.
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # COUNT(*) returns the number of rows
        cursor.execute("SELECT COUNT(*) as total FROM employees")
        
        result = cursor.fetchone()
        count = result[0]  # Extract count from tuple
        
        cursor.close()
        
        return {
            "success": True,
            "count": count
        }
        
    except Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        if connection.is_connected():
            connection.close()
```

**2. Add endpoint in main.py:**
```python
@app.get("/employees/count")
def get_employee_count():
    """
    Get total number of employees.
    
    Returns the count of all employees in the database.
    """
    result = employee_queries.get_employee_count()
    
    if result["success"]:
        return {"count": result["count"]}
    else:
        raise HTTPException(status_code=500, detail=result["error"])
```

**Test:**
- GET `http://localhost:8000/employees/count`
- Should return: `{"count": 3}`

---

### Task 2: Add Department List Endpoint

**Goal:** Create endpoint that returns list of all unique departments.

**Requirements:**
- Endpoint: GET `/employees/departments`
- Returns: `{"departments": ["Engineering", "Marketing", "Sales"]}`

**Solution:**

**1. Add function in employee_queries.py:**
```python
def get_all_departments():
    """
    Returns list of all unique departments.
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # SELECT DISTINCT returns unique values only
        cursor.execute("""
            SELECT DISTINCT department 
            FROM employees 
            ORDER BY department
        """)
        
        # Extract department names from tuples
        departments = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        
        return {
            "success": True,
            "departments": departments
        }
        
    except Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        if connection.is_connected():
            connection.close()
```

**2. Add endpoint in main.py:**
```python
@app.get("/employees/departments")
def get_departments():
    """
    Get list of all unique departments.
    
    Returns a list of all departments that have employees.
    """
    result = employee_queries.get_all_departments()
    
    if result["success"]:
        return {
            "count": len(result["departments"]),
            "departments": result["departments"]
        }
    else:
        raise HTTPException(status_code=500, detail=result["error"])
```

**Test:**
- GET `http://localhost:8000/employees/departments`
- Should return: `{"count": 3, "departments": ["Engineering", "HR", "Marketing"]}`

---

## ✅ Verification Checklist

Before moving to Stage 5, verify:

- [ ] `employee_queries.py` created with all CRUD functions
- [ ] `main.py` updated with all endpoints
- [ ] Email validation package installed
- [ ] Can create employee via POST
- [ ] Can get all employees via GET
- [ ] Can get single employee by ID
- [ ] Can update employee via PUT
- [ ] Can delete employee
- [ ] Can search employees
- [ ] Pydantic validation works (try invalid data)
- [ ] Error handling works (try non-existent ID)
- [ ] Both practice tasks completed

---

## 🐛 Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'employee_queries'"

**Cause:** Import error or file not in same directory

**Solution:**
- Ensure `employee_queries.py` is in same folder as `main.py`
- Check file name spelling (no typos)
- Restart uvicorn server

---

### Issue 2: "connection.commit() raises 'NoneType' error"

**Cause:** Connection failed but code tries to use it

**Solution:**
Always check connection before using:
```python
connection = get_db_connection()
if not connection:
    return {"success": False, "error": "Connection failed"}
```

---

### Issue 3: Email validation not working

**Cause:** pydantic[email] not installed

**Solution:**
```powershell
pip install "pydantic[email]"
```

---

### Issue 4: "422 Unprocessable Entity" for valid data

**Cause:** Data type mismatch

**Common mistakes:**
- Sending salary as string: `"salary": "75000"` ❌
- Should be number: `"salary": 75000` ✅

**Check Postman:**
- Body type is set to "raw"
- Type is set to "JSON"

---

### Issue 5: Changes not persisting in database

**Cause:** Forgot to call connection.commit()

**Solution:**
After INSERT, UPDATE, DELETE:
```python
cursor.execute("INSERT INTO employees ...")
connection.commit()  # Don't forget this!
```

---

## 📚 Key Takeaways

### What You Learned

1. **CRUD Operations:**
   - Create (INSERT)
   - Read (SELECT)
   - Update (UPDATE)
   - Delete (DELETE)

2. **SQL Security:**
   - SQL injection dangers
   - Parameterized queries
   - Never use f-strings for SQL

3. **FastAPI Integration:**
   - Pydantic models for validation
   - HTTP status codes
   - Error handling with HTTPException

4. **Database Best Practices:**
   - Always close connections
   - Use dictionary cursor for APIs
   - Call commit() for data changes
   - Check if records exist before operations

5. **API Design:**
   - RESTful endpoints
   - Proper HTTP methods
   - Meaningful error messages
   - Input validation

---

## 🚀 Next Steps - Stage 5

In Stage 5, we will add file operations:
- ✅ Create and write text files
- ✅ Read files (complete and line by line)
- ✅ Append to files
- ✅ Check file existence
- ✅ Rename, copy, and delete files
- ✅ Get file size and metadata

---

## 📚 Additional Resources

- SQL Injection Prevention: https://owasp.org/www-community/attacks/SQL_Injection
- HTTP Status Codes: https://httpstatuses.com/
- Pydantic Documentation: https://docs.pydantic.dev/
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- REST API Best Practices: https://restfulapi.net/

---

**🎉 Congratulations!** You now have a fully functional employee management API!

**When you're ready, type "stage 5"** and we'll add file handling capabilities! 📄
