import mysql.connector
import hashlib
from datetime import datetime

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sthelosothando@04',
    'database': 'Final_Year_Project'
}

def create_admin_user():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if admin already exists
        cursor.execute("SELECT * FROM admins WHERE email = 'admin@gofundmeconnect.com'")
        existing_admin = cursor.fetchone()

        if existing_admin:
            print("Admin user already exists!")
            return

        # Create admin user
        full_name = "System Administrator"
        email = "admin@gofundmeconnect.com"
        password = "admin123" 
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute(
            "INSERT INTO admins (full_name, email, password, created_at) VALUES (%s, %s, %s, %s)",
            (full_name, email, hashed_password, datetime.now())
        )

        conn.commit()
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("Please change the password after first login.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_admin_user()
