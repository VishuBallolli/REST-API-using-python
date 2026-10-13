# employee_queries.py
# This file contains all SQL queries and database operations for employee management
# CRUD = Create, Read, Update, Delete

from database import get_db_connection
from mysql.connector import Error


def create_employee(name, email, department, salary):
    """
    Creates a new employee in the database.
    
    Args:
        name (str): Employee name
        email (str): Employee email (must be unique)
        department (str): Department name
        salary (float): Employee salary
        
    Returns:
        dict: Success message with employee ID, or error message
        
    Example:
        result = create_employee("John Doe", "john@company.com", "Engineering", 75000)
        # Returns: {"success": True, "id": 1, "message": "Employee created"}
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # SQL INSERT query with placeholders (%s) for safety
        # NEVER use f-strings for SQL queries - prevents SQL injection!
        insert_query = """
        INSERT INTO employees (name, email, department, salary)
        VALUES (%s, %s, %s, %s)
        """
        
        # Data tuple - values are automatically escaped by mysql-connector
        employee_data = (name, email, department, salary)
        
        # Execute the query
        cursor.execute(insert_query, employee_data)
        
        # Commit the transaction - saves changes to database
        # Without commit, changes are lost!
        connection.commit()
        
        # Get the auto-generated employee ID
        employee_id = cursor.lastrowid
        
        cursor.close()
        
        return {
            "success": True,
            "id": employee_id,
            "message": f"Employee created successfully with ID {employee_id}"
        }
        
    except Error as e:
        # Check for duplicate email error
        if e.errno == 1062:  # MySQL error code for duplicate entry
            return {
                "success": False,
                "error": "Email already exists"
            }
        else:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }
            
    finally:
        # Always close the connection, even if error occurs
        if connection.is_connected():
            connection.close()


def get_all_employees():
    """
    Retrieves all employees from the database.
    
    Returns:
        dict: Success with list of employees, or error message
        
    Example:
        result = get_all_employees()
        # Returns: {
        #     "success": True,
        #     "count": 2,
        #     "employees": [
        #         {"id": 1, "name": "John", "email": "john@company.com", ...},
        #         {"id": 2, "name": "Jane", "email": "jane@company.com", ...}
        #     ]
        # }
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        # dictionary=True makes results come back as dictionaries
        # Instead of tuples, which is more convenient for JSON APIs
        cursor = connection.cursor(dictionary=True)
        
        # SQL SELECT query to get all employees
        select_query = """
        SELECT id, name, email, department, salary, created_at, updated_at
        FROM employees
        ORDER BY id DESC
        """
        
        cursor.execute(select_query)
        
        # Fetch all results as a list of dictionaries
        employees = cursor.fetchall()
        
        cursor.close()
        
        return {
            "success": True,
            "count": len(employees),
            "employees": employees
        }
        
    except Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        if connection.is_connected():
            connection.close()


def get_employee_by_id(employee_id):
    """
    Retrieves a specific employee by their ID.
    
    Args:
        employee_id (int): The employee's ID
        
    Returns:
        dict: Success with employee data, or error if not found
        
    Example:
        result = get_employee_by_id(1)
        # Returns: {
        #     "success": True,
        #     "employee": {"id": 1, "name": "John", ...}
        # }
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # SQL SELECT query with WHERE clause
        # %s is a placeholder for safe parameter binding
        select_query = """
        SELECT id, name, email, department, salary, created_at, updated_at
        FROM employees
        WHERE id = %s
        """
        
        cursor.execute(select_query, (employee_id,))
        
        # Fetch one result (or None if not found)
        employee = cursor.fetchone()
        
        cursor.close()
        
        if employee:
            return {
                "success": True,
                "employee": employee
            }
        else:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
    except Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        if connection.is_connected():
            connection.close()


def update_employee(employee_id, name=None, email=None, department=None, salary=None):
    """
    Updates an employee's information.
    Only updates fields that are provided (not None).
    
    Args:
        employee_id (int): The employee's ID
        name (str, optional): New name
        email (str, optional): New email
        department (str, optional): New department
        salary (float, optional): New salary
        
    Returns:
        dict: Success message or error
        
    Example:
        # Update only salary
        result = update_employee(1, salary=80000)
        
        # Update name and department
        result = update_employee(1, name="John Smith", department="Sales")
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        # First, check if employee exists
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        
        if not cursor.fetchone():
            cursor.close()
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        update_values = []
        
        if name is not None:
            update_fields.append("name = %s")
            update_values.append(name)
            
        if email is not None:
            update_fields.append("email = %s")
            update_values.append(email)
            
        if department is not None:
            update_fields.append("department = %s")
            update_values.append(department)
            
        if salary is not None:
            update_fields.append("salary = %s")
            update_values.append(salary)
        
        # If no fields to update, return error
        if not update_fields:
            cursor.close()
            return {
                "success": False,
                "error": "No fields provided to update"
            }
        
        # Construct the UPDATE query
        update_query = f"""
        UPDATE employees
        SET {', '.join(update_fields)}
        WHERE id = %s
        """
        
        # Add employee_id to the end of values list
        update_values.append(employee_id)
        
        # Execute the update
        cursor.execute(update_query, tuple(update_values))
        connection.commit()
        
        cursor.close()
        
        return {
            "success": True,
            "message": f"Employee {employee_id} updated successfully"
        }
        
    except Error as e:
        # Check for duplicate email error
        if e.errno == 1062:
            return {
                "success": False,
                "error": "Email already exists"
            }
        else:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }
            
    finally:
        if connection.is_connected():
            connection.close()


def delete_employee(employee_id):
    """
    Deletes an employee from the database.
    
    Args:
        employee_id (int): The employee's ID
        
    Returns:
        dict: Success message or error
        
    Example:
        result = delete_employee(1)
        # Returns: {"success": True, "message": "Employee deleted"}
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # First, check if employee exists
        cursor.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        
        if not cursor.fetchone():
            cursor.close()
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        # SQL DELETE query
        delete_query = "DELETE FROM employees WHERE id = %s"
        
        cursor.execute(delete_query, (employee_id,))
        connection.commit()
        
        cursor.close()
        
        return {
            "success": True,
            "message": f"Employee {employee_id} deleted successfully"
        }
        
    except Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        if connection.is_connected():
            connection.close()


def search_employees(search_term, search_by="name"):
    """
    Searches for employees by name or department.
    Uses LIKE operator for partial matching.
    
    Args:
        search_term (str): The term to search for
        search_by (str): Field to search in ("name" or "department")
        
    Returns:
        dict: Success with list of matching employees, or error
        
    Example:
        # Find all employees with "John" in their name
        result = search_employees("John", "name")
        
        # Find all employees in "Engineering"
        result = search_employees("Eng", "department")
    """
    connection = get_db_connection()
    
    if not connection:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        # Validate search_by parameter to prevent SQL injection
        if search_by not in ["name", "department"]:
            return {
                "success": False,
                "error": "Invalid search field. Use 'name' or 'department'"
            }
        
        cursor = connection.cursor(dictionary=True)
        
        # SQL LIKE query for partial matching
        # %term% means "anything before, term, anything after"
        search_query = f"""
        SELECT id, name, email, department, salary, created_at, updated_at
        FROM employees
        WHERE {search_by} LIKE %s
        ORDER BY id DESC
        """
        
        # Add wildcards for LIKE operator
        search_pattern = f"%{search_term}%"
        
        cursor.execute(search_query, (search_pattern,))
        employees = cursor.fetchall()
        
        cursor.close()
        
        return {
            "success": True,
            "count": len(employees),
            "search_term": search_term,
            "search_by": search_by,
            "employees": employees
        }
        
    except Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        if connection.is_connected():
            connection.close()


# Test functions - run this file directly to test
if __name__ == "__main__":
    print("Testing Employee Query Functions")
    print("=" * 50)
    
    # Test 1: Create employee
    print("\n1. Creating employee...")
    result = create_employee(
        name="Test User",
        email="test@company.com",
        department="Testing",
        salary=60000.00
    )
    print(result)
    
    # Test 2: Get all employees
    print("\n2. Getting all employees...")
    result = get_all_employees()
    print(f"Found {result.get('count', 0)} employees")
    
    # Test 3: Search employees
    print("\n3. Searching for 'Test'...")
    result = search_employees("Test", "name")
    print(f"Found {result.get('count', 0)} matches")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
