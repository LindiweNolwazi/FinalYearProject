import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sthelosothando@04",
        database="Final_Year_Project"
    )

def update_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Add new columns to students table
        alter_queries = [
            "ALTER TABLE students ADD COLUMN student_number VARCHAR(50)",
            "ALTER TABLE students ADD COLUMN gender VARCHAR(10)",
            "ALTER TABLE students ADD COLUMN campus VARCHAR(100)",
            "ALTER TABLE students ADD COLUMN qualification VARCHAR(100)",
            "ALTER TABLE students ADD COLUMN faculty VARCHAR(100)",
            "ALTER TABLE students ADD COLUMN year_level VARCHAR(20)",
            "ALTER TABLE students ADD COLUMN expected_completion DATE",
            "ALTER TABLE students ADD COLUMN gpa DECIMAL(3,2)"
        ]

        for query in alter_queries:
            cursor.execute(query)
            print(f"Executed: {query}")

        conn.commit()
        cursor.close()
        conn.close()
        print("Schema updated successfully!")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_schema()
