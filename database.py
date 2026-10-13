# database.py
# This file handles all database connection logic
# It creates and manages the connection to MySQL database

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads the .env file and makes variables available via os.getenv()
load_dotenv()

# Database configuration loaded from environment variables
# This keeps sensitive data (like passwords) out of the code
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),      # Database server address
    "user": os.getenv("DB_USER", "root"),           # MySQL username
    "password": os.getenv("DB_PASSWORD", ""),       # MySQL password (from .env)
    "database": os.getenv("DB_NAME", "employee_db"), # Database name
    "port": int(os.getenv("DB_PORT", 3306))         # MySQL port (default 3306)
}


def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.

    This function attempts to connect to MySQL using the credentials
    from the .env file. If successful, it returns the connection object.
    If it fails, it prints an error and returns None.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
        None: If connection fails

    Example usage:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Execute queries...
            connection.close()
    """
    try:
        # Attempt to establish connection to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)

        # Check if connection was successful
        if connection.is_connected():
            # Get MySQL server information
            db_info = connection.get_server_info()
            print(f"✅ Successfully connected to MySQL Server version {db_info}")
            return connection

    except Error as e:
        # If connection fails, print detailed error message
        print(f"❌ Error connecting to MySQL: {e}")
        return None


def test_connection():
    """
    Tests the database connection by connecting and fetching MySQL version.

    This is a utility function to verify that:
    1. MySQL credentials are correct
    2. Database server is running
    3. Python can connect to MySQL

    Returns:
        bool: True if connection successful, False otherwise
    """
    connection = get_db_connection()

    if connection:
        try:
            # Create a cursor object to execute queries
            cursor = connection.cursor()

            # Execute a simple query to check connection
            cursor.execute("SELECT VERSION()")

            # Fetch the result
            version = cursor.fetchone()
            print(f"📊 MySQL Database Version: {version[0]}")

            # Close cursor
            cursor.close()
            return True

        except Error as e:
            print(f"❌ Error executing query: {e}")
            return False

        finally:
            # Always close the connection when done
            if connection.is_connected():
                connection.close()
                print("🔌 MySQL connection closed")
    else:
        return False


def create_database():
    """
    Creates the employee_db database if it doesn't exist.

    This function:
    1. Connects to MySQL without specifying a database
    2. Creates the employee_db database
    3. Handles the case where database already exists

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Connect without specifying database
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database if it doesn't exist
            database_name = DB_CONFIG["database"]
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"✅ Database '{database_name}' created successfully (or already exists)")

            cursor.close()
            connection.close()
            return True

    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False


def create_employees_table():
    """
    Creates the employees table in the database.

    Table structure:
    - id: Primary key, auto-increment
    - name: Employee name (required, max 100 chars)
    - email: Employee email (required, unique, max 100 chars)
    - department: Department name (required, max 50 chars)
    - salary: Employee salary (required, decimal with 2 decimal places)

    Returns:
        bool: True if successful, False otherwise
    """
    connection = get_db_connection()

    if connection:
        try:
            cursor = connection.cursor()

            # SQL query to create employees table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                department VARCHAR(50) NOT NULL,
                salary DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """

            # Execute the query
            cursor.execute(create_table_query)
            print("✅ Table 'employees' created successfully (or already exists)")

            cursor.close()
            return True

        except Error as e:
            print(f"❌ Error creating table: {e}")
            return False

        finally:
            if connection.is_connected():
                connection.close()
    else:
        return False


def initialize_database():
    """
    Complete database initialization:
    1. Creates database
    2. Creates employees table
    3. Verifies setup

    This is the main function to call when setting up the project.
    Run this once during initial setup.

    Returns:
        bool: True if all steps successful, False otherwise
    """
    print("🚀 Starting database initialization...")
    print("-" * 50)

    # Step 1: Create database
    print("\n📁 Step 1: Creating database...")
    if not create_database():
        print("❌ Failed to create database")
        return False

    # Step 2: Test connection
    print("\n🔌 Step 2: Testing database connection...")
    if not test_connection():
        print("❌ Failed to connect to database")
        return False

    # Step 3: Create employees table
    print("\n📊 Step 3: Creating employees table...")
    if not create_employees_table():
        print("❌ Failed to create employees table")
        return False

    print("\n" + "=" * 50)
    print("🎉 Database initialization completed successfully!")
    print("=" * 50)
    return True


# This block runs when you execute: python database.py
# It's useful for initial setup and testing
if __name__ == "__main__":
    # Run the complete database initialization
    initialize_database()
