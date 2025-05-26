import sqlite3
import os

# Path to the SQL file exported from DBDesigner.net
sql_file_path = "HospitalInformationSystem_TP2-1747346443.sql"
# New database name
db_file_path = "hospital_design.db"

def execute_sql_script(sql_file_path, db_file_path):
    """Execute the SQL script to create the new database structure."""
    if not os.path.exists(sql_file_path):
        print(f"SQL file not found: {sql_file_path}")
        return
    
    # Connect to the new SQLite database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    try:
        # Read the SQL script
        with open(sql_file_path, "r") as file:
            sql_script = file.read()

        # Execute the script
        cursor.executescript(sql_script)
        conn.commit()
        print(f"Database structure created successfully in {db_file_path}.")
    
    except sqlite3.Error as e:
        print(f"Error executing SQL script: {e}")
    
    finally:
        cursor.close()
        conn.close()

# Execute the function
execute_sql_script(sql_file_path, db_file_path)