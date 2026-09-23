import hashlib
import json
import os
import random
from io import BytesIO

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, send_file, url_for
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from werkzeug.security import check_password_hash, generate_password_hash

# NOTE: Mock Blockchain class is included as the original was not provided.
class Blockchain:
    def __init__(self, db):
        self.db = db

    # FIX 1: Updated to accept cert_json
    def add_block(self, cert_id, cert_json): 
        # Mock logic: Insert a new mock block
        try:
            cursor = self.db.cursor()
            
            # In a real app, this would calculate a hash based on the previous block and the certificate data
            mock_prev_hash = "0" * 64 
            
            # FIX 2: Calculate the hash using the actual certificate data (cert_json)
            mock_current_hash = hashlib.sha256(cert_json.encode()).hexdigest()
            
            cursor.execute("INSERT INTO blockchain (certificate_id, previous_hash, current_hash) VALUES (%s, %s, %s)",
                           (cert_id, mock_prev_hash, mock_current_hash))
            self.db.commit()
            return True
        except Exception as e:
            # print(f"Error adding block: {e}")
            return False

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------- Database Connection -------------------
def get_db_connection():
    # Using the database name 'changee' from your uploaded code
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="changee" 
    )

def generate_unique_cert_id():
    """Generates a unique AR-prefixed 6-digit certificate ID."""
    db = get_db_connection()
    cursor = db.cursor()
    while True:
        # Generate a random 6-digit number
        cert_num = random.randint(100000, 999999)
        cert_id = f"AR{cert_num}"
        # Check for uniqueness in the database
        cursor.execute("SELECT id FROM certificates WHERE id = %s", (cert_id,))
        if not cursor.fetchone():
            return cert_id

# ------------------- Home & Login -------------------
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        # Fetch account_status and name for login check and session storage
        cursor.execute("SELECT id, name, email, password, role, account_status FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            # CHECK: account_status for login permission
            if user['account_status'] == 'approved' or user['role'] == 'admin':
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['user_name'] = user['name'] # Store name in session
                flash("Login successful!", "success")
                if user['role'] == "admin":
                    return redirect(url_for("dashboard_admin"))
                elif user['role'] == "institution":
                    return redirect(url_for("dashboard_institution"))
                elif user['role'] == "student":
                    return redirect(url_for("dashboard_student"))
                elif user['role'] == "verifier":
                    return redirect(url_for("dashboard_verifier"))
            elif user['account_status'] == 'pending':
                flash("Your account is pending admin approval. You cannot log in yet.", "warning")
            elif user['account_status'] == 'hold':
                flash("Your account is currently on hold. Contact administrator.", "warning")
            elif user['account_status'] == 'rejected':
                flash("Your account registration has been rejected. Please contact administrator.", "danger")
            else:
                flash("Invalid credentials or account status unknown!", "danger")
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html")

# ------------------- Register -------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))
        
        # Set account_status: Admin is auto-approved, others are pending.
        account_status = 'approved' if role == 'admin' else 'pending'

        # Insert into users, including 'account_status'
        cursor.execute("INSERT INTO users (name,email,password,role,account_status) VALUES (%s,%s,%s,%s,%s)",
                       (name, email, password, role, account_status))
        db.commit()
        user_id = cursor.lastrowid

        # Insert into institutions if role=institution
        if role == "institution":
            # The institution's status defaults to 'pending'
            cursor.execute("INSERT INTO institutions (id, name, status) VALUES (%s,%s,%s)",
                           (user_id, name, 'pending'))
            db.commit()

        if account_status == 'pending':
            flash(f"Registration successful! Your account is now **pending admin approval**. You will be able to login once approved.", "success")
        else:
            flash("Admin account created! Please login.", "success")
            
        return redirect(url_for("login"))
    return render_template("register.html")

# ------------------- Dashboards -------------------
@app.route("/dashboard/admin")
def dashboard_admin():
    if session.get('role') != "admin":
        return redirect(url_for("login"))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Determine the current section for dynamic loading (default is 'main')
    section = request.args.get('section', 'main')
    
    # --- 1. Global Stats (Always required for sidebar/main dashboard) ---
    stats = {}
    cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role != 'admin'")
    stats['total_users'] = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) AS pending_users FROM users WHERE account_status = 'pending'")
    stats['pending_users'] = cursor.fetchone()['pending_users']

    cursor.execute("SELECT COUNT(*) AS total_certs FROM certificates")
    stats['total_certs'] = cursor.fetchone()['total_certs']

    cursor.execute("SELECT COUNT(*) AS valid_verifications FROM verifications WHERE result = 'valid'")
    stats['valid_verifications'] = cursor.fetchone()['valid_verifications']

    cursor.execute("SELECT COUNT(*) AS invalid_verifications FROM verifications WHERE result = 'invalid'")
    stats['invalid_verifications'] = cursor.fetchone()['invalid_verifications']
    
    # --- 2. Section-Specific Data Fetching ---
    data = {}
    
    if section == 'users':
        # User Management Data
        cursor.execute("SELECT id, name, email, role, account_status FROM users WHERE role!='admin' ORDER BY id DESC")
        data['all_users'] = cursor.fetchall()

    elif section == 'tampered':
        # Tampered Data (invalid verifications)
        cursor.execute("""
            SELECT 
                v.id AS verification_id, 
                c.id AS certificate_id, 
                c.course_name, 
                u_student.name AS student_name,
                u_verifier.name AS verifier_name,
                v.verified_at
            FROM verifications v
            JOIN certificates c ON v.certificate_id = c.id
            JOIN users u_student ON c.student_id = u_student.id
            JOIN users u_verifier ON v.verifier_id = u_verifier.id
            WHERE v.result = 'invalid'
            ORDER BY v.verified_at DESC
        """)
        data['tampered_certs'] = cursor.fetchall()

    elif section == 'verified':
        # Verified Data (valid verifications)
        cursor.execute("""
            SELECT 
                v.id AS verification_id, 
                c.id AS certificate_id, 
                c.course_name, 
                u_student.name AS student_name,
                u_verifier.name AS verifier_name,
                v.verified_at
            FROM verifications v
            JOIN certificates c ON v.certificate_id = c.id
            JOIN users u_student ON c.student_id = u_student.id
            JOIN users u_verifier ON v.verifier_id = u_verifier.id
            WHERE v.result = 'valid'
            ORDER BY v.verified_at DESC
        """)
        data['verified_certs'] = cursor.fetchall()
        
    db.close()
    
    # Pass all data to the template
    return render_template("dashboard_admin.html", section=section, stats=stats, **data)

@app.route("/dashboard/institution")
def dashboard_institution():
    if session.get('role') != "institution":
        return redirect(url_for("login"))
    
    institution_id = session['user_id']
    # Get institution name from session, assuming it was stored at login
    institution_name = session.get('user_name', 'Institution User') 
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # 1. Fetch all certificates issued by this institution
    cursor.execute("""
        SELECT 
            c.*, 
            u.name AS student_name 
        FROM certificates c 
        JOIN users u ON c.student_id = u.id 
        WHERE c.institution_id = %s
        ORDER BY c.issue_year DESC, c.id DESC
    """, (institution_id,))
    certificates = cursor.fetchall()
    
    # 2. Calculate Total Certificates Issued
    total_certs_issued = len(certificates)
    
    # 3. Calculate Total Students Certified (Unique student IDs in the certificates)
    cursor.execute("SELECT COUNT(DISTINCT student_id) AS total_students FROM certificates WHERE institution_id = %s", (institution_id,))
    total_students_certified = cursor.fetchone()['total_students']
    
    # NOTE: Logic for 'All Approved Students (System)' is intentionally removed.
    
    db.close()
    
    # Pass the dynamic data and the institution name to the template
    return render_template(
        "dashboard_institution.html", 
        institution_name=institution_name,
        certificates=certificates, 
        total_certs_issued=total_certs_issued,
        total_students_certified=total_students_certified
    )

@app.route("/dashboard/student")
def dashboard_student():
    if session.get('role') != "student":
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM certificates WHERE student_id = %s", (session['user_id'],))
    certificates = cursor.fetchall()
    return render_template("dashboard_student.html", certificates=certificates)

@app.route("/dashboard/verifier")
def dashboard_verifier():
    if session.get('role') != "verifier":
        return redirect(url_for("login"))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Fetch current user details
    cursor.execute("SELECT id, name, email, role FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()
    if not user:
        flash("User data not found!", "danger")
        return redirect(url_for("logout"))
        
    section = request.args.get('section', 'main')
    
    # Initialize variables for the dashboard view
    total_verified = 0
    valid_count = 0
    invalid_count = 0
    recent_verifications = []

    if section == 'main':
        verifier_id = session['user_id']
        
        # Quick Stats: Certificates Verified (Total)
        cursor.execute("SELECT COUNT(*) AS total_verified FROM verifications WHERE verifier_id = %s", (verifier_id,))
        total_verified = cursor.fetchone().get('total_verified') or 0

        # Quick Stats: Valid Certificates
        cursor.execute("SELECT COUNT(*) AS valid_count FROM verifications WHERE verifier_id = %s AND result = 'valid'", (verifier_id,))
        valid_count = cursor.fetchone().get('valid_count') or 0

        # Quick Stats: Invalid Certificates
        cursor.execute("SELECT COUNT(*) AS invalid_count FROM verifications WHERE verifier_id = %s AND result = 'invalid'", (verifier_id,))
        invalid_count = cursor.fetchone().get('invalid_count') or 0
        
        # Recent Verification Activity (fetch 10 most recent)
        cursor.execute("""
            SELECT 
                v.id, 
                c.id AS cert_id, 
                c.course_name, 
                v.result, 
                v.verified_at, 
                u_inst.name AS institution_name, 
                u_stud.name AS student_name
            FROM verifications v
            JOIN certificates c ON v.certificate_id = c.id
            JOIN users u_stud ON c.student_id = u_stud.id
            JOIN users u_inst ON c.institution_id = u_inst.id
            WHERE v.verifier_id = %s
            ORDER BY v.verified_at DESC
            LIMIT 10
        """, (verifier_id,))
        recent_verifications = cursor.fetchall()
    
    db.close()
    
    return render_template(
        "dashboard_verifier.html", 
        user=user, 
        section=section,
        total_verified=total_verified,
        valid_count=valid_count,
        invalid_count=invalid_count,
        recent_verifications=recent_verifications
    )

# --- Admin User Action (Handles all status changes) ---
@app.route("/admin_user_action/<int:user_id>/<string:action>")
def admin_user_action(user_id, action):
    if session.get('role') != "admin":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("login"))

    # VALID ACTIONS: approved, rejected, hold, pending
    if action not in ['approved', 'rejected', 'hold', 'pending']: 
        flash("Invalid action specified.", "danger")
        return redirect(url_for("dashboard_admin"))

    db = get_db_connection()
    cursor = db.cursor()
    
    # 1. Update the user's main account_status in the users table
    cursor.execute("UPDATE users SET account_status=%s WHERE id=%s", (action, user_id))
    
    # 2. If it's an institution being approved/rejected, update the institutions table's status as well
    cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    user_role = cursor.fetchone()
    
    if user_role and user_role[0] == 'institution':
        if action == 'approved':
            # Also update the secondary 'institutions' table status and approved_by
            cursor.execute("UPDATE institutions SET status='approved', approved_by=%s WHERE id=%s", (session['user_id'], user_id))
        elif action == 'rejected':
            # Also update the secondary 'institutions' table status
            cursor.execute("UPDATE institutions SET status='rejected', approved_by=NULL WHERE id=%s", (user_id,))
            
    db.commit()
    flash(f"User (ID: {user_id}) status set to '{action}' successfully.", "success")
    return redirect(url_for("dashboard_admin", section='users')) # Redirect back to user management

# --- Admin Delete Action ---
@app.route("/admin_user_delete/<int:user_id>")
def admin_user_delete(user_id):
    if session.get('role') != "admin":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("login"))

    if user_id == session['user_id']:
        flash("Security Alert: You cannot delete your own admin account.", "danger")
        return redirect(url_for("dashboard_admin", section='users'))

    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Deletes the user and relies on database foreign keys (ON DELETE CASCADE) to clean up related records 
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        db.commit()
        if cursor.rowcount > 0:
            flash(f"User (ID: {user_id}) and all related records deleted successfully.", "success")
        else:
            flash(f"User (ID: {user_id}) not found or could not be deleted.", "warning")
    except Exception as e:
        flash(f"Database Error: Could not delete user. Error: {e}", "danger")
    
    return redirect(url_for("dashboard_admin", section='users'))

# ------------------- Approve Institution (Redirect to generic action) -------------------
@app.route("/approve_institution/<int:inst_id>")
def approve_institution(inst_id):
    return redirect(url_for("admin_user_action", user_id=inst_id, action='approved'))


# ------------------- Issue Certificate -------------------
@app.route("/issue_certificate", methods=["GET", "POST"])
def issue_certificate():
    if session.get('role') != "institution":
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()
    # Fetch only students who have an 'approved' account status
    cursor.execute("SELECT id, name FROM users WHERE role='student' AND account_status='approved'")
    students = cursor.fetchall()

    if request.method == "POST":
        student_id = request.form['student_id']
        course_name = request.form['course_name']
        cgpa = request.form['cgpa']
        issue_year = request.form['issue_year']
        roll_number = request.form['roll_number']
        father_name = request.form['father_name']
        mother_name = request.form['mother_name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        year_of_joining = request.form['year_of_joining']

        # Get the student's name based on their ID
        cursor.execute("SELECT name FROM users WHERE id = %s", (student_id,))
        student_name = cursor.fetchone()[0]

        # Generate a unique certificate ID
        cert_id = generate_unique_cert_id()

        # Create the certificate data as JSON
        certificate_data = {
            "id": cert_id,
            "student_id": student_id,
            "student_name": student_name,
            "institution_id": session['user_id'],
            "course_name": course_name,
            "cgpa": cgpa,
            "issue_year": issue_year,
            "roll_number": roll_number,
            "father_name": father_name,
            "mother_name": mother_name,
            "gender": gender,
            "mobile_number": mobile_number,
            "year_of_joining": year_of_joining
        }
        cert_json = json.dumps(certificate_data) # Store this for both DB and Hashing

        # Generate PDF content and store it in a variable
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        # Personalized header based on user's saved information (Argroup Solutions)
        institution_name = "Argroup Solutions Institution" 
        story.append(Paragraph(f"{institution_name}", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Certificate of Achievement", styles['h2']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"This is to certify that:", styles['Normal']))
        story.append(Paragraph(f"<b>Name:</b> {certificate_data['student_name']}", styles['Normal']))
        story.append(Paragraph(f"<b>Roll Number:</b> {certificate_data['roll_number']}", styles['Normal']))
        story.append(Paragraph(f"<b>Father's Name:</b> {certificate_data['father_name']}", styles['Normal']))
        story.append(Paragraph(f"<b>Mother's Name:</b> {certificate_data['mother_name']}", styles['Normal']))
        story.append(Paragraph(f"<b>Gender:</b> {certificate_data['gender']}", styles['Normal']))
        story.append(Paragraph(f"<b>Mobile Number:</b> {certificate_data['mobile_number']}", styles['Normal']))
        story.append(Paragraph(f"<b>Year of Joining:</b> {certificate_data['year_of_joining']}", styles['Normal']))
        story.append(Paragraph(f"<b>Course:</b> {certificate_data['course_name']}", styles['Normal']))
        story.append(Paragraph(f"<b>CGPA:</b> {certificate_data['cgpa']}", styles['Normal']))
        story.append(Paragraph(f"<b>Issue Year:</b> {certificate_data['issue_year']}", styles['Normal']))
        doc.build(story)
        pdf_content = buffer.getvalue()

        # Insert into certificates table with the new ID and PDF content
        cursor.execute("""
            INSERT INTO certificates (id, student_id, institution_id, course_name, cgpa, issue_year, roll_number, father_name, mother_name, gender, mobile_number, year_of_joining, certificate_data, pdf_content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (cert_id, student_id, session['user_id'], course_name, cgpa, issue_year, roll_number, father_name, mother_name, gender, mobile_number, year_of_joining, cert_json, pdf_content))
        db.commit()

        # Add to blockchain using the new custom ID
        blockchain = Blockchain(db)
        # FIX 3: Pass cert_json to the updated add_block method
        if blockchain.add_block(cert_id, cert_json): 
            flash(f"Certificate issued successfully with ID: {cert_id}", "success")
        else:
            flash("Error issuing certificate.", "danger")

        return redirect(url_for('issue_certificate'))

    return render_template("issue_certificate.html", students=students)

# ------------------- Certificate PDF Generation -------------------
@app.route("/download_certificate/<string:cert_id>")
def download_certificate(cert_id):
    # FIX: Ensure only logged-in users who are institutions or students can download.
    # The original logic was correct, but let's ensure session is checked first.
    if session.get('role') not in ["student", "verifier", "institution"]:
        flash("Access denied. Please log in.", "danger")
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Fetch the stored PDF content
    # NOTE: The browser opens the PDF in a new tab, which shouldn't cause a logout.
    # The issue might be a session cookie problem not correctly being sent with the new tab request.
    # By ensuring the route is correctly protected, we minimize risk.
    cursor.execute("SELECT pdf_content FROM certificates WHERE id=%s", (cert_id,))
    cert = cursor.fetchone()

    if not cert or not cert['pdf_content']:
        flash("Certificate not found or PDF content is missing.", "danger")
        return redirect(url_for("dashboard_institution")) # Redirect back to institution dashboard

    pdf_content = cert['pdf_content']
    return send_file(BytesIO(pdf_content), as_attachment=True, download_name=f'certificate_{cert_id}.pdf', mimetype='application/pdf')

# ------------------- Verify Certificate -------------------
@app.route("/verify_certificate", methods=["GET", "POST"])
def verify_certificate():
    result = None
    sound_file = None
    if session.get('role') != "verifier":
        return redirect(url_for("login"))

    if request.method == "POST":
        cert_id = request.form['certificate_id']
        uploaded_pdf = request.files['certificate_pdf']  # Get the uploaded file
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # 1. Check if the certificate ID exists in the database.
        cursor.execute("SELECT pdf_content, certificate_data FROM certificates WHERE id=%s", (cert_id,))
        cert = cursor.fetchone()

        if cert:
            # Certificate ID is valid, proceed with verification.
            
            # 2. Verify PDF content.
            uploaded_pdf_bytes = uploaded_pdf.read()
            original_pdf_bytes = cert['pdf_content']
            pdf_match = uploaded_pdf_bytes == original_pdf_bytes
            
            # 3. Verify blockchain hash.
            cert_json = cert['certificate_data']
            # This is correct: Calculates the hash of the stored JSON data
            calc_hash = hashlib.sha256(cert_json.encode()).hexdigest()
            
            cursor.execute("SELECT current_hash FROM blockchain WHERE certificate_id=%s", (cert_id,))
            block = cursor.fetchone()
            # This comparison now correctly compares the real data hash against the stored hash
            hash_match = (block and block['current_hash'] == calc_hash) 

            # 4. Determine final result based on both checks.
            if pdf_match and hash_match:
                result = "valid"
                flash("Certificate is valid! The PDF content and blockchain hash match.", "success")
                sound_file = '1.mp3'
            else:
                result = "invalid"
                if not pdf_match:
                    flash("Reason: The uploaded PDF content does not match the original.", "danger")
                if not hash_match:
                    flash("Reason: The blockchain hash does not match, indicating potential data tampering.", "danger")
                sound_file = '2.mp3'
            
            # Record the verification result
            cursor.execute("INSERT INTO verifications (verifier_id, certificate_id, result) VALUES (%s, %s, %s)",
                           (session['user_id'], cert_id, result))
            db.commit()
            
        else:
            # The certificate ID is not in the database.
            result = "invalid"
            flash("Invalid certificate ID. No matching certificate found.", "danger")
            sound_file = '2.mp3'

    return render_template("verify_certificate.html", result=result, sound_file=sound_file)


# ------------------- Logout -------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# ------------------- Run App -------------------
if __name__ == "__main__":
    app.run(debug=True)