import paypalrestsdk
import hashlib
import urllib.parse
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity, get_jwt
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
from functools import wraps
import os
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def jwt_required_with_role(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()

                if role and claims.get("role") != role:
                    return jsonify({"error": f"{role} access required"}), 403

                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": "Invalid or expired token"}), 401
        return decorator
    return wrapper

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "GoFundMe2025"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=25)
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # Gmail SMTP server
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "gofundmeconnect2025@gmail.com"  
app.config["MAIL_PASSWORD"] = "Gofundme2025" 
app.config["MAIL_DEFAULT_SENDER"] = "gofundmeconnect2025@gmail.com"

# PayPal configuration
app.config['PAYPAL_MODE'] = 'sandbox'  # sandbox or live
app.config['PAYPAL_CLIENT_ID'] = 'YOUR_PAYPAL_CLIENT_ID'
app.config['PAYPAL_CLIENT_SECRET'] = 'YOUR_PAYPAL_CLIENT_SECRET'

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": app.config['PAYPAL_MODE'],
    "client_id": app.config['PAYPAL_CLIENT_ID'],
    "client_secret": app.config['PAYPAL_CLIENT_SECRET']
})

# PayFast configuration
app.config['PAYFAST_MERCHANT_ID'] = 'YOUR_PAYFAST_MERCHANT_ID'
app.config['PAYFAST_MERCHANT_KEY'] = 'YOUR_PAYFAST_MERCHANT_KEY'
app.config['PAYFAST_PASS_PHRASE'] = 'YOUR_PAYFAST_PASSPHRASE'  # Optional

jwt = JWTManager(app)

# Make datetime available globally in templates
app.jinja_env.globals.update(datetime=datetime)

import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sthelosothando@04",
        database="Final_Year_Project"
    )

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/admin-login")
def admin_login():
    return render_template("admin-login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin-dashboard.html")

@app.route("/student-login")
def student_login():
    return render_template("student-login.html")

@app.route("/student-register")
def student_register():
    return render_template("student-register.html")

@app.route("/student-dashboard")
def student_dashboard():
    return render_template("student-dashboard.html")

# SRC Application Page Route
@app.route("/apply-src")
def apply_src():
    return render_template("apply-src.html")

# External Sponsorship Application Page Route
@app.route("/apply-external")
def apply_external():
    return render_template("apply-external.html")

@app.route("/sponsor-login")
def sponsor_login():
    return render_template("sponsor-login.html")

@app.route("/sponsor-register")
def sponsor_register():
    return render_template("sponsor-register.html")

@app.route("/sponsor-dashboard")
def sponsor_dashboard():
    return render_template("sponsor-dashboard.html")

@app.route("/student-forgot-password")
def student_forgot_password():
    return render_template("student-forgot-password.html")

@app.route("/sponsor-forgot-password")
def sponsor_forgot_password():
    return render_template("sponsor-forgot-password.html")

# Informational Pages
@app.route("/actors")
def actors():
    return render_template("actors.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

#Auth API Endpoints
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        role = data.get("role")
        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")

        # Validate required fields
        if not all([role, full_name, email, password]):
            logger.error("Missing required fields in registration request")
            return jsonify({"error": "Missing required fields"}), 400

        # Validate email format
        if "@" not in email or "." not in email:
            logger.error(f"Invalid email format: {email}")
            return jsonify({"error": "Invalid email format"}), 400

        # Validate student email domain
        if role == "student" and not email.endswith("@stu.unizulu.ac.za"):
            logger.error(f"Invalid student email domain: {email}")
            return jsonify({"error": "Students must use a university email address (@stu.unizulu.ac.za)"}), 400

        # Validate password strength
        if len(password) < 6:
            logger.error("Password too short for registration")
            return jsonify({"error": "Password must be at least 6 characters long"}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db_connection()
        cursor = conn.cursor()

        if role == "student":
            cellphone_number = data.get("cellphone_number", "")
            student_number = data.get("student_number", "")
            gender = data.get("gender", "")
            campus = data.get("campus", "")
            qualification = data.get("qualification", "")
            faculty = data.get("faculty", "")
            year_level = data.get("year_level", "")
            expected_completion = data.get("expected_completion", None)
            gpa = data.get("gpa", None)

            # Validate student-specific fields
            if not student_number:
                logger.error("Student number is required for student registration")
                return jsonify({"error": "Student number is required"}), 400

            # Validate cellphone number format (South African numbers only)
            if cellphone_number:
                if not cellphone_number.isdigit() or len(cellphone_number) != 10:
                    logger.error(f"Invalid cellphone number length: {cellphone_number}")
                    return jsonify({"error": "Cellphone number must be exactly 10 digits"}), 400
                if not cellphone_number.startswith(('06', '07', '08')):
                    logger.error(f"Invalid cellphone number prefix: {cellphone_number}")
                    return jsonify({"error": "Cellphone number must start with 06, 07, or 08 (South African numbers only)"}), 400

            cursor.execute(
                "INSERT INTO students (name, email, password, cellphone_number, student_number, gender, campus, qualification, faculty, year_level, expected_completion, gpa, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (full_name, email, hashed_password, cellphone_number, student_number, gender, campus, qualification, faculty, year_level, expected_completion, gpa, datetime.now())
            )
            logger.info(f"New student registered: {email}")
        elif role == "sponsor":
            organization = data.get("organization", "")
            cursor.execute(
                "INSERT INTO sponsors (sponsor_name, email, password, organization, created_at) VALUES (%s, %s, %s, %s, %s)",
                (full_name, email, hashed_password, organization, datetime.now())
            )
            logger.info(f"New sponsor registered: {email}")
        elif role == "admin":
            # Admin registration-
            cursor.execute(
                "INSERT INTO admins (full_name, email, password, created_at) VALUES (%s, %s, %s, %s)",
                (full_name, email, hashed_password, datetime.now())
            )
            logger.info(f"New admin registered: {email}")
        else:
            logger.error(f"Invalid role attempted: {role}")
            return jsonify({"error": "Invalid role"}), 400

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": f"{role} registered successfully"}), 201

    except mysql.connector.Error as err:
        logger.error(f"Database error in register: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in register: {e}")
        return jsonify({"error": f"Server error: {e}"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        role = data.get("role")
        email = data.get("email")
        password = data.get("password")

        if not all([role, email, password]):
            logger.error("Missing required fields in login request")
            return jsonify({"error": "Missing required fields"}), 400

        # Validate email format
        if "@" not in email or "." not in email:
            logger.error(f"Invalid email format in login: {email}")
            return jsonify({"error": "Invalid email format"}), 400

        # Validate student email domain
        if role == "student" and not email.endswith("@stu.unizulu.ac.za"):
            logger.error(f"Invalid student email domain in login: {email}")
            return jsonify({"error": "Students must use a university email address (@stu.unizulu.ac.za)"}), 400

        # Validate password strength
        if len(password) < 6:
            logger.error("Password too short for login attempt")
            return jsonify({"error": "Password must be at least 6 characters long"}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if role == "student":
            cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, hashed_password))
            user = cursor.fetchone()
            id_field = "student_id"
        elif role == "sponsor":
            cursor.execute("SELECT * FROM sponsors WHERE email=%s AND password=%s", (email, hashed_password))
            user = cursor.fetchone()
            id_field = "sponsor_id"
        elif role == "admin":
            cursor.execute("SELECT * FROM admins WHERE email=%s AND password=%s", (email, hashed_password))
            user = cursor.fetchone()
            id_field = "admin_id"
        else:
            logger.error(f"Invalid role attempted in login: {role}")
            return jsonify({"error": "Invalid role"}), 400

        cursor.close()
        conn.close()

        if not user:
            logger.warning(f"Failed login attempt for {role}: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=str(user[id_field]), additional_claims={
            "role": role,
            "email": email
        })

        user.pop("password", None)

        logger.info(f"Successful login for {role}: {email}")
        return jsonify({
            "access_token": access_token,
            "user": user,
            "role": role
        })


    except mysql.connector.Error as err:
        logger.error(f"Database error in login: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in login: {e}")
        return jsonify({"error": f"Server error: {e}"}), 500

# Funding Opportunities
@app.route("/funding/list", methods=["GET"])
@jwt_required_with_role()
def funding_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT fo.*, a.full_name as posted_by_name 
            FROM funding_opportunities fo 
            LEFT JOIN admins a ON fo.posted_by = a.admin_id 
            WHERE fo.deadline >= CURDATE()
            ORDER BY fo.created_at DESC
        """)
        opportunities = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(opportunities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Student Applications
@app.route("/student/applications", methods=["GET"])
@jwt_required_with_role("student")
def student_applications():
    try:
        # Get student ID from JWT identity
        student_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT a.*, f.title, f.deadline, f.funding_type, f.funding_amount
            FROM applications a
            JOIN funding_opportunities f ON a.opportunity_id = f.opportunity_id
            WHERE a.student_id = %s
            ORDER BY a.applied_at DESC
        """, (student_id,))

        applications = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(applications)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get SRC funding opportunities
@app.route("/funding/src", methods=["GET"])
@jwt_required_with_role()
def src_funding_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT fo.*, a.full_name as posted_by_name
            FROM funding_opportunities fo
            LEFT JOIN admins a ON fo.posted_by = a.admin_id
            WHERE fo.deadline >= CURDATE() AND fo.funding_type = 'SRC'
            ORDER BY fo.created_at DESC
        """)
        opportunities = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(opportunities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get external sponsorship opportunities
@app.route("/funding/external", methods=["GET"])
@jwt_required_with_role()
def external_funding_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT fo.*, a.full_name as posted_by_name
            FROM funding_opportunities fo
            LEFT JOIN admins a ON fo.posted_by = a.admin_id
            WHERE fo.deadline >= CURDATE() AND fo.funding_type = 'External'
            ORDER BY fo.created_at DESC
        """)
        opportunities = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(opportunities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/student/apply", methods=["POST"])
@jwt_required_with_role("student")
def student_apply():
    try:
        # Get student ID from JWT identity
        student_id = get_jwt_identity()

        # Try to get opportunity_id from JSON first, then form data
        opportunity_id = None
        if request.is_json:
            data = request.get_json()
            opportunity_id = data.get("opportunity_id")
        else:
            opportunity_id = request.form.get("opportunity_id")

        if not opportunity_id:
            return jsonify({"error": "Opportunity ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if application already exists
        cursor.execute(
            "SELECT * FROM applications WHERE student_id = %s AND opportunity_id = %s",
            (student_id, opportunity_id)
        )
        existing_application = cursor.fetchone()

        if existing_application:
            return jsonify({"error": "You have already applied for this opportunity"}), 400

        # Create new application
        cursor.execute(
            "INSERT INTO applications (student_id, opportunity_id, status) VALUES (%s, %s, %s)",
            (student_id, opportunity_id, "pending")
        )
        application_id = cursor.lastrowid

        # Handle file uploads
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        document_types = ['id_document', 'transcript', 'admission_letter', 'supporting_document']
        for doc_type in document_types:
            file = request.files.get(doc_type)
            if file and file.filename:
                filename = secure_filename(f"{student_id}_{doc_type}_{file.filename}")
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

                # Insert document record
                cursor.execute(
                    "INSERT INTO documents (student_id, type, file_url, uploaded_at) VALUES (%s, %s, %s, %s)",
                    (student_id, doc_type, f"static/uploads/{filename}", datetime.now())
                )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Application submitted successfully"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/student/notifications", methods=["GET"])
@jwt_required_with_role("student")
def student_notifications():
    try:
        # Get student ID from JWT identity
        student_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT notification_id, message, created_at, is_read
            FROM notifications
            WHERE student_id = %s
            ORDER BY created_at DESC
        """, (student_id,))

        notifications = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(notifications)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/student/notifications/mark-read", methods=["POST"])
@jwt_required_with_role("student")
def mark_notification_read():
    try:
        # Get student ID from JWT identity
        student_id = get_jwt_identity()

        data = request.get_json()
        notification_id = data.get("notification_id")

        if not notification_id:
            return jsonify({"error": "Notification ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update notification to read
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE notification_id = %s AND student_id = %s",
            (notification_id, student_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Notification marked as read"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/student/profile", methods=["GET", "PUT"])
@jwt_required_with_role("student")
def student_profile():
    try:
        # Get student ID from JWT identity
        student_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == "GET":
            cursor.execute("""
                SELECT name as full_name, email, cellphone_number as contact_number, student_number, gender, campus, qualification, faculty, year_level, expected_completion, gpa
                FROM students
                WHERE student_id = %s
            """, (student_id,))

            student = cursor.fetchone()
            cursor.close()
            conn.close()

            if not student:
                return jsonify({"error": "Student not found"}), 404

            # Add default values for fields that might not be in the database
            profile_data = {
                "full_name": student.get("full_name", ""),
                "student_number": student.get("student_number", ""),
                "email": student.get("email", ""),
                "contact_number": student.get("contact_number", ""),
                "gender": student.get("gender", ""),
                "campus": student.get("campus", ""),
                "qualification": student.get("qualification", ""),
                "faculty": student.get("faculty", ""),
                "year_level": student.get("year_level", ""),
                "expected_completion": student.get("expected_completion", ""),
                "gpa": student.get("gpa", "")
            }

            return jsonify(profile_data)

        elif request.method == "PUT":
            data = request.get_json()
            full_name = data.get("full_name")
            email = data.get("email")
            contact_number = data.get("contact_number")
            gender = data.get("gender")
            campus = data.get("campus")
            qualification = data.get("qualification")
            faculty = data.get("faculty")
            year_level = data.get("year_level")
            expected_completion = data.get("expected_completion")
            gpa = data.get("gpa")

            # Validate student email domain
            if email and not email.endswith("@stu.unizulu.ac.za"):
                logger.error(f"Invalid student email domain in profile update: {email}")
                return jsonify({"error": "Students must use a university email address (@stu.unizulu.ac.za)"}), 400

            # Update the student profile
            cursor.execute("""
                UPDATE students
                SET name = %s, email = %s, cellphone_number = %s, gender = %s, campus = %s, qualification = %s, faculty = %s, year_level = %s, expected_completion = %s, gpa = %s
                WHERE student_id = %s
            """, (full_name, email, contact_number, gender, campus, qualification, faculty, year_level, expected_completion, gpa, student_id))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Profile updated successfully"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Sponsor Transactions
@app.route("/sponsor/transactions", methods=["GET"])
@jwt_required_with_role("sponsor")
def sponsor_transactions():
    try:
        # Get sponsor ID from JWT identity
        sponsor_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.*, s.name as student_name, fo.title
            FROM transactions t
            JOIN students s ON t.student_id = s.student_id
            JOIN funding_opportunities fo ON t.opportunity_id = fo.opportunity_id
            WHERE t.sponsor_id = %s
            ORDER BY t.created_at DESC
        """, (sponsor_id,))

        transactions = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(transactions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sponsor/approved-students", methods=["GET"])
@jwt_required_with_role("sponsor")
def sponsor_approved_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT a.application_id, a.student_id, a.opportunity_id, a.status, a.applied_at,
                   s.name as student_name, s.email as student_email, s.cellphone_number, s.student_number, s.gender, s.campus, s.qualification, s.faculty, s.year_level, s.expected_completion, s.gpa,
                   f.title as opportunity_title, f.funding_amount as need
            FROM applications a
            JOIN students s ON a.student_id = s.student_id
            JOIN funding_opportunities f ON a.opportunity_id = f.opportunity_id
            WHERE a.status = 'approved'
            ORDER BY a.applied_at DESC
        """)

        approved_students = cursor.fetchall()

        # For each approved student, fetch documents
        for student in approved_students:
            cursor.execute(
                "SELECT type, file_url FROM documents WHERE student_id = %s",
                (student['student_id'],)
            )
            documents = cursor.fetchall()
            student['documents'] = documents

        cursor.close()
        conn.close()

        return jsonify(approved_students)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sponsor/student-details", methods=["POST"])
@jwt_required_with_role("sponsor")
def get_student_details():
    try:
        data = request.get_json()
        student_name = data.get("student_name")

        if not student_name:
            return jsonify({"error": "Student name is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # First try to find the student in approved applications
        cursor.execute("""
            SELECT a.application_id, a.student_id, a.opportunity_id, a.status, a.applied_at,
                   s.name as student_name, s.email as student_email, s.cellphone_number, s.student_number, s.gender, s.campus, s.qualification, s.faculty, s.year_level, s.expected_completion, s.gpa,
                   f.title as opportunity_title, f.funding_amount as need
            FROM applications a
            JOIN students s ON a.student_id = s.student_id
            JOIN funding_opportunities f ON a.opportunity_id = f.opportunity_id
            WHERE a.status = 'approved' AND s.name = %s
            ORDER BY a.applied_at DESC
            LIMIT 1
        """, (student_name,))

        student = cursor.fetchone()

        if not student:
            # If not found in approved applications, look for any student with that name
            cursor.execute("""
                SELECT student_id, name as student_name, email as student_email, cellphone_number, student_number, gender, campus, qualification, faculty, year_level, expected_completion, gpa
                FROM students
                WHERE name = %s
                LIMIT 1
            """, (student_name,))

            student = cursor.fetchone()
            if student:
                # Set default values for students not in approved applications
                student['opportunity_id'] = ''
                student['need'] = 0
                student['opportunity_title'] = 'Custom Funding'

        # Fetch documents for the student
        if student:
            cursor.execute(
                "SELECT type, file_url FROM documents WHERE student_id = %s",
                (student['student_id'],)
            )
            documents = cursor.fetchall()
            student['documents'] = documents

        cursor.close()
        conn.close()

        if not student:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(student)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sponsor/fund", methods=["POST"])
@jwt_required_with_role("sponsor")
def sponsor_fund():
    try:
        # Get sponsor ID from JWT identity
        sponsor_id = int(get_jwt_identity())

        data = request.get_json()
        student_id = int(data.get("student_id"))
        opportunity_id = int(data.get("opportunity_id"))
        amount = float(data.get("amount"))

        if not all([data.get("student_id"), data.get("opportunity_id"), data.get("amount")]):
            return jsonify({"error": "Student ID, Opportunity ID, and Amount are required"}), 400

        # Validate amount is positive
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if sponsor exists
        cursor.execute("SELECT sponsor_id FROM sponsors WHERE sponsor_id = %s", (sponsor_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Sponsor not found"}), 404

        # Check if student exists
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        # Check if opportunity exists
        cursor.execute("SELECT opportunity_id FROM funding_opportunities WHERE opportunity_id = %s", (opportunity_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Funding opportunity not found"}), 404

        # Check if student application is approved for this opportunity
        cursor.execute("SELECT status FROM applications WHERE student_id = %s AND opportunity_id = %s", (student_id, opportunity_id))
        app = cursor.fetchone()
        if not app or app[0] != 'approved':
            return jsonify({"error": "Student application not approved for this opportunity"}), 403

        # Create transaction
        cursor.execute(
            """INSERT INTO transactions
            (sponsor_id, student_id, opportunity_id, amount, payment_method, status)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (sponsor_id, student_id, opportunity_id, amount, "Online", "pending")
        )

        transaction_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        # Return transaction_id so frontend can redirect to payment page
        return jsonify({
            "message": "Funding request submitted successfully",
            "transaction_id": transaction_id,
            "payment_url": f"/payment/{transaction_id}"
        }), 201

    except ValueError as ve:
        return jsonify({"error": f"Invalid data type: {ve}"}), 400
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/payment/<int:transaction_id>")
@jwt_required_with_role("sponsor")
def payment_page(transaction_id):
    try:
        sponsor_id = int(get_jwt_identity())

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.*, s.name as student_name, fo.title as opportunity_title
            FROM transactions t
            JOIN students s ON t.student_id = s.student_id
            JOIN funding_opportunities fo ON t.opportunity_id = fo.opportunity_id
            WHERE t.transaction_id = %s AND t.sponsor_id = %s AND t.status = 'pending'
        """, (transaction_id, sponsor_id))

        transaction = cursor.fetchone()
        cursor.close()
        conn.close()

        if not transaction:
            return jsonify({"error": "Transaction not found or not authorized"}), 404

        return render_template("payment.html", transaction=transaction)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Alternative endpoint for AJAX requests to get payment page data
@app.route("/payment/data/<int:transaction_id>")
@jwt_required_with_role("sponsor")
def payment_page_data(transaction_id):
    try:
        sponsor_id = int(get_jwt_identity())

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.*, s.name as student_name, fo.title as opportunity_title
            FROM transactions t
            JOIN students s ON t.student_id = s.student_id
            JOIN funding_opportunities fo ON t.opportunity_id = fo.opportunity_id
            WHERE t.transaction_id = %s AND t.sponsor_id = %s AND t.status = 'pending'
        """, (transaction_id, sponsor_id))

        transaction = cursor.fetchone()
        cursor.close()
        conn.close()

        if not transaction:
            return jsonify({"error": "Transaction not found or not authorized"}), 404

        return jsonify({
            "transaction_id": transaction["transaction_id"],
            "student_name": transaction["student_name"],
            "opportunity_title": transaction["opportunity_title"],
            "amount": transaction["amount"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/payment/paypal/initiate/<int:transaction_id>", methods=["POST"])
@jwt_required_with_role("sponsor")
def initiate_paypal_payment(transaction_id):
    try:
        sponsor_id = int(get_jwt_identity())

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.*, s.name as student_name, fo.title as opportunity_title
            FROM transactions t
            JOIN students s ON t.student_id = s.student_id
            JOIN funding_opportunities fo ON t.opportunity_id = fo.opportunity_id
            WHERE t.transaction_id = %s AND t.sponsor_id = %s AND t.status = 'pending'
        """, (transaction_id, sponsor_id))

        transaction = cursor.fetchone()
        cursor.close()
        conn.close()

        if not transaction:
            return jsonify({"error": "Transaction not found or not authorized"}), 404

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.host_url + "payment/paypal/return",
                "cancel_url": request.host_url + "payment/paypal/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": transaction['opportunity_title'],
                        "sku": str(transaction['transaction_id']),
                        "price": f"{transaction['amount']:.2f}",
                        "currency": "ZAR",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{transaction['amount']:.2f}",
                    "currency": "ZAR"
                },
                "description": f"Funding for student {transaction['student_name']}"
            }]
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
            # Save PayPal payment ID to transaction for later verification
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET payment_method = %s, paypal_payment_id = %s WHERE transaction_id = %s",
                           ("PayPal", payment.id, transaction_id))
            conn.commit()
            cursor.close()
            conn.close()

            # Redirect user to PayPal approval URL
            return redirect(approval_url)
        else:
            return jsonify({"error": "Failed to create PayPal payment"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/payment/paypal/return")
def paypal_return():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    if not payment_id or not payer_id:
        return redirect("/sponsor-dashboard?error=payment_failed")

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Update transaction status to completed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET status = 'completed' WHERE paypal_payment_id = %s", (payment_id,))
        cursor.execute("SELECT student_id, amount FROM transactions WHERE paypal_payment_id = %s", (payment_id,))
        transaction = cursor.fetchone()
        if transaction:
            student_id, amount = transaction
            cursor.execute(
                "INSERT INTO notifications (student_id, message, created_at) VALUES (%s, %s, %s)",
                (student_id, f"You have received funding of R{amount} via PayPal.", datetime.now())
            )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/sponsor-dashboard?success=payment_completed")
    else:
        return redirect("/sponsor-dashboard?error=payment_execution_failed")

@app.route("/payment/paypal/cancel")
def paypal_cancel():
    return redirect("/sponsor-dashboard?info=payment_cancelled")

@app.route("/payment/payfast/initiate/<int:transaction_id>", methods=["POST"])
@jwt_required_with_role("sponsor")
def initiate_payfast_payment(transaction_id):
    try:
        sponsor_id = int(get_jwt_identity())

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.*, s.name as student_name, fo.title as opportunity_title
            FROM transactions t
            JOIN students s ON t.student_id = s.student_id
            JOIN funding_opportunities fo ON t.opportunity_id = fo.opportunity_id
            WHERE t.transaction_id = %s AND t.sponsor_id = %s AND t.status = 'pending'
        """, (transaction_id, sponsor_id))

        transaction = cursor.fetchone()
        cursor.close()
        conn.close()

        if not transaction:
            return jsonify({"error": "Transaction not found or not authorized"}), 404

        # Prepare PayFast payment data
        payfast_data = {
            'merchant_id': app.config['PAYFAST_MERCHANT_ID'],
            'merchant_key': app.config['PAYFAST_MERCHANT_KEY'],
            'return_url': request.host_url + 'payment/payfast/return',
            'cancel_url': request.host_url + 'payment/payfast/cancel',
            'notify_url': request.host_url + 'payment/payfast/notify',
            'name_first': 'Sponsor',
            'name_last': 'User',
            'email_address': 'sponsor@example.com',
            'm_payment_id': str(transaction_id),
            'amount': f"{transaction['amount']:.2f}",
            'item_name': transaction['opportunity_title'],
            'item_description': f"Funding for student {transaction['student_name']}",
            'custom_str1': str(sponsor_id)
        }

        # Generate signature
        def generate_signature(data):
            data = {k: v for k, v in sorted(data.items()) if v}
            signature_string = '&'.join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in data.items())
            if app.config.get('PAYFAST_PASS_PHRASE'):
                signature_string += f"&passphrase={urllib.parse.quote_plus(app.config['PAYFAST_PASS_PHRASE'])}"
            return hashlib.md5(signature_string.encode('utf-8')).hexdigest()

        signature = generate_signature(payfast_data)
        payfast_data['signature'] = signature

        # Save PayFast payment data in transaction (optional)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET payment_method = %s WHERE transaction_id = %s",
                       ("PayFast", transaction_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(payfast_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/payment/payfast/return")
def payfast_return():
    return redirect("/sponsor-dashboard?success=payment_completed")

@app.route("/payment/payfast/cancel")
def payfast_cancel():
    return redirect("/sponsor-dashboard?info=payment_cancelled")

@app.route("/payment/payfast/notify", methods=["POST"])
def payfast_notify():
    try:
        data = request.form.to_dict()
        signature = data.pop('signature', None)

        def generate_signature(data):
            data = {k: v for k, v in sorted(data.items()) if v}
            signature_string = '&'.join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in data.items())
            if app.config.get('PAYFAST_PASS_PHRASE'):
                signature_string += f"&passphrase={urllib.parse.quote_plus(app.config['PAYFAST_PASS_PHRASE'])}"
            return hashlib.md5(signature_string.encode('utf-8')).hexdigest()

        generated_signature = generate_signature(data)

        if signature != generated_signature:
            return "Invalid signature", 400

        # Verify payment status
        payment_status = data.get('payment_status')
        transaction_id = int(data.get('m_payment_id'))

        if payment_status == 'COMPLETE':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status = 'completed' WHERE transaction_id = %s", (transaction_id,))
            cursor.execute("SELECT student_id, amount FROM transactions WHERE transaction_id = %s", (transaction_id,))
            transaction = cursor.fetchone()
            if transaction:
                student_id, amount = transaction
                cursor.execute(
                    "INSERT INTO notifications (student_id, message, created_at) VALUES (%s, %s, %s)",
                    (student_id, f"You have received funding of R{amount} via PayFast.", datetime.now())
                )
            conn.commit()
            cursor.close()
            conn.close()

        return "OK", 200

    except Exception as e:
        return str(e), 500

# Admin Functions
@app.route("/admin/funding/create", methods=["POST"])
@app.route("/admin/post-opportunity", methods=["POST"])
@jwt_required_with_role("admin")
def admin_create_funding():
    try:
        # Get admin ID from JWT identity (it's stored as string, so keep as string for database)
        admin_id = get_jwt_identity()

        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        funding_amount = data.get("funding_amount")
        funding_type = data.get("funding_type")
        eligibility_criteria = data.get("eligibility_criteria")
        deadline = data.get("deadline")

        if not all([title, description, funding_amount, funding_type, deadline]):
            return jsonify({"error": "All fields are required"}), 400

        # Convert funding_amount to float to ensure proper decimal handling
        try:
            funding_amount = float(funding_amount)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid funding amount format"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO funding_opportunities
            (title, description, funding_amount, funding_type, eligibility_criteria, posted_by, deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (title, description, funding_amount, funding_type, eligibility_criteria, admin_id, deadline)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Funding opportunity posted successfully"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/applications", methods=["GET"])
@jwt_required_with_role("admin")
def admin_applications():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT a.application_id, a.student_id, a.opportunity_id, a.status, a.applied_at,
                   s.name as student_name, s.email as student_email,
                   f.title as opportunity_title
            FROM applications a
            JOIN students s ON a.student_id = s.student_id
            JOIN funding_opportunities f ON a.opportunity_id = f.opportunity_id
            ORDER BY a.applied_at DESC
        """)

        applications = cursor.fetchall()

        # For each application, fetch documents
        for app in applications:
            cursor.execute(
                "SELECT type, file_url FROM documents WHERE student_id = %s",
                (app['student_id'],)
            )
            documents = cursor.fetchall()
            app['documents'] = documents

        cursor.close()
        conn.close()

        return jsonify(applications)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/approve-application", methods=["POST"])
@jwt_required_with_role("admin")
def admin_approve_application():
    try:
        data = request.get_json()
        application_id = data.get("application_id")

        if not application_id:
            logger.error("Application ID is missing in request")
            return jsonify({"error": "Application ID is required"}), 400

        try:
            application_id = int(application_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid application_id: {application_id}")
            return jsonify({"error": "Application ID must be a valid integer"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update application status to approved
        cursor.execute(
            "UPDATE applications SET status = 'approved' WHERE application_id = %s AND status = 'pending'",
            (application_id,)
        )

        if cursor.rowcount == 0:
            logger.warning(f"Application {application_id} not found or already processed")
            return jsonify({"error": "Application not found or already processed"}), 404

        # Get student_id for notification
        cursor.execute("SELECT student_id FROM applications WHERE application_id = %s", (application_id,))
        student = cursor.fetchone()
        if student:
            cursor.execute(
                "INSERT INTO notifications (student_id, message, created_at) VALUES (%s, %s, %s)",
                (student[0], "Your application has been approved.", datetime.now())
            )
            logger.info(f"Notification sent for approved application {application_id}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Application {application_id} approved successfully")
        return jsonify({"message": "Application approved successfully"}), 200

    except mysql.connector.Error as err:
        logger.error(f"Database error in approve_application: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in approve_application: {e}")
        return jsonify({"error": f"Server error: {e}"}), 500

@app.route("/admin/reject-application", methods=["POST"])
@jwt_required_with_role("admin")
def admin_reject_application():
    try:
        data = request.get_json()
        application_id = data.get("application_id")

        if not application_id:
            logger.error("Application ID is missing in request")
            return jsonify({"error": "Application ID is required"}), 400

        try:
            application_id = int(application_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid application_id: {application_id}")
            return jsonify({"error": "Application ID must be a valid integer"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update application status to rejected
        cursor.execute(
            "UPDATE applications SET status = 'rejected' WHERE application_id = %s AND status = 'pending'",
            (application_id,)
        )

        if cursor.rowcount == 0:
            logger.warning(f"Application {application_id} not found or already processed")
            return jsonify({"error": "Application not found or already processed"}), 404

        # Get student_id for notification
        cursor.execute("SELECT student_id FROM applications WHERE application_id = %s", (application_id,))
        student = cursor.fetchone()
        if student:
            cursor.execute(
                "INSERT INTO notifications (student_id, message, created_at) VALUES (%s, %s, %s)",
                (student[0], "Your application has been rejected.", datetime.now())
            )
            logger.info(f"Notification sent for rejected application {application_id}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Application {application_id} rejected successfully")
        return jsonify({"message": "Application rejected successfully"}), 200

    except mysql.connector.Error as err:
        logger.error(f"Database error in reject_application: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in reject_application: {e}")
        return jsonify({"error": f"Server error: {e}"}), 500

@app.route("/admin/funding/list", methods=["GET"])
@jwt_required_with_role("admin")
def admin_funding_list():
    try:
        # Get admin ID from JWT identity
        admin_id = int(get_jwt_identity())

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM funding_opportunities
            WHERE posted_by = %s
            ORDER BY created_at DESC
        """, (admin_id,))
        opportunities = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(opportunities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/reports", methods=["GET"])
@jwt_required_with_role("admin")
def admin_reports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total students
        cursor.execute("SELECT COUNT(*) as total_students FROM students")
        total_students = cursor.fetchone()['total_students']

        # Total sponsors
        cursor.execute("SELECT COUNT(*) as total_sponsors FROM sponsors")
        total_sponsors = cursor.fetchone()['total_sponsors']

        # Total funding opportunities
        cursor.execute("SELECT COUNT(*) as total_opportunities FROM funding_opportunities")
        total_opportunities = cursor.fetchone()['total_opportunities']

        # Total amount sponsored
        cursor.execute("SELECT SUM(amount) as total_amount FROM transactions WHERE status = 'completed'")
        total_amount = cursor.fetchone()['total_amount'] or 0

        cursor.close()
        conn.close()

        return jsonify({
            "total_students": total_students,
            "total_sponsors": total_sponsors,
            "total_opportunities": total_opportunities,
            "total_amount_sponsored": float(total_amount)
        })

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Diagnostic Routes 
@app.route('/debug/check-files')
def debug_check_files():
    import json
    
    # Check critical files
    files_to_check = [
        'templates/home.html',
        'templates/admin-login.html',
        'templates/admin-dashboard.html',
        'templates/student-login.html',
        'templates/student-register.html',
        'templates/student-dashboard.html',
        'templates/sponsor-login.html',
        'templates/sponsor-register.html',
        'templates/sponsor-dashboard.html',
        'templates/actors.html',
        'templates/contact.html',
        'templates/privacy.html',
        'templates/terms.html',
        'templates/faq.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    results = {}
    for file_path in files_to_check:
        full_path = os.path.join(app.root_path, file_path)
        exists = os.path.exists(full_path)
        readable = os.access(full_path, os.R_OK) if exists else False
        results[file_path] = {
            'exists': exists,
            'readable': readable,
            'full_path': full_path
        }
    
    return jsonify(results)

@app.route('/debug/static-test')
def debug_static_test():
    """Test if static file serving works"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Static File Test</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    </head>
    <body>
        <h1>Static File Test</h1>
        <p>If this page has styles, static files are working.</p>
        <p>Check console for any 404 errors.</p>
        <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    </body>
    </html>
    '''

@app.route('/debug/routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(routes)

@app.route('/debug/db-connection')
def debug_db_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "connected"})
    except Exception as e:
        return jsonify({"status": "disconnected", "error": str(e)}), 500

import uuid
from flask import url_for, redirect, flash

# Password Reset Request Route
@app.route("/password-reset/request", methods=["POST"])
def password_reset_request():
    try:
        role = request.form.get("role")
        email = request.form.get("email")

        if not role or not email:
            return "Role and email are required", 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if user exists based on role
        if role == "student":
            cursor.execute("SELECT student_id as user_id, email FROM students WHERE email = %s", (email,))
        elif role == "sponsor":
            cursor.execute("SELECT sponsor_id as user_id, email FROM sponsors WHERE email = %s", (email,))
        else:
            return "Invalid role", 400

        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return "User not found", 404

        # Generate token and expiration (1 hour)
        token = str(uuid.uuid4())
        expiration = datetime.now() + timedelta(hours=1)

        # Store token in password_reset_tokens table
        cursor.execute(
            "INSERT INTO password_reset_tokens (user_id, role, token, expiration) VALUES (%s, %s, %s, %s)",
            (user["user_id"], role, token, expiration)
        )
        conn.commit()

        # Send password reset email
        reset_link = url_for("password_reset_form", token=token, _external=True)

        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email
        msg['Subject'] = "Password Reset Request"

        body = f"Hello,\n\nYou have requested to reset your password for your {role} account.\n\nClick the following link to reset your password:\n{reset_link}\n\nThis link will expire in 1 hour.\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nGoFundMe Connect Team"

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            server.set_debuglevel(1)  # Enable SMTP debug output
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            text = msg.as_string()
            server.sendmail(app.config['MAIL_DEFAULT_SENDER'], email, text)
            server.quit()
        except Exception as e:
            # For now, continue as if sent, but in production, handle error

            cursor.close()
        conn.close()

        return "Password reset email sent", 200

    except Exception as e:
        return str(e), 500

# Password Reset Form Route
@app.route("/password-reset/<token>", methods=["GET"])
def password_reset_form(token):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM password_reset_tokens WHERE token = %s AND expiration > %s",
            (token, datetime.now())
        )
        token_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not token_data:
            return "Invalid or expired token", 400

        return render_template("reset-password.html", token=token)

    except Exception as e:
        return str(e), 500

# Password Reset Submission Route
@app.route("/password-reset/<token>", methods=["POST"])
def password_reset_submit(token):
    try:
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not password or not confirm_password:
            return "Password and confirm password are required", 400

        if password != confirm_password:
            return "Passwords do not match", 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM password_reset_tokens WHERE token = %s AND expiration > %s",
            (token, datetime.now())
        )
        token_data = cursor.fetchone()

        if not token_data:
            cursor.close()
            conn.close()
            return "Invalid or expired token", 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Update password in the appropriate table
        if token_data["role"] == "student":
            cursor.execute(
                "UPDATE students SET password = %s WHERE student_id = %s",
                (hashed_password, token_data["user_id"])
            )
        elif token_data["role"] == "sponsor":
            cursor.execute(
                "UPDATE sponsors SET password = %s WHERE sponsor_id = %s",
                (hashed_password, token_data["user_id"])
            )
        else:
            cursor.close()
            conn.close()
            return "Invalid role", 400

        # Delete the token after use
        cursor.execute(
            "DELETE FROM password_reset_tokens WHERE token = %s",
            (token,)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return "Password has been reset successfully", 200

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
