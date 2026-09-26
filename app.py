from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = "scholarship.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLES ----------------

def create_tables():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            college TEXT NOT NULL,
            percentage TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            aadhaar TEXT,
            income_certificate TEXT,
            caste_certificate TEXT,
            marks_memo TEXT,
            bank_passbook TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            scholarship TEXT,
            academic_score TEXT,
            income TEXT,
            category TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SCHOLARSHIPS ----------------

@app.route("/scholarships")
def scholarships():
    return render_template("scholarships.html")


# ---------------- ELIGIBILITY ----------------

@app.route("/eligibility")
def eligibility():
    return render_template("eligibility.html")


# ---------------- PROFILE ----------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        name = request.form["name"]
        student_id = request.form["student_id"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        college = request.form["college"]
        percentage = request.form["percentage"]

        conn = get_db_connection()

        try:

            conn.execute("""
                INSERT INTO students
                (
                    name,
                    student_id,
                    email,
                    phone,
                    course,
                    college,
                    percentage
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                student_id,
                email,
                phone,
                course,
                college,
                percentage
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Student ID already exists."

        conn.close()

        return render_template(
            "profile.html",
            success="Profile saved successfully!"
        )

    return render_template("profile.html")


# ---------------- DOCUMENTS ----------------

@app.route("/documents", methods=["GET", "POST"])
def documents():

    if request.method == "POST":

        student_id = request.form.get("student_id", "")

        aadhaar = request.files.get("aadhaar")
        income_certificate = request.files.get("income_certificate")
        caste_certificate = request.files.get("caste_certificate")
        marks_memo = request.files.get("marks_memo")
        bank_passbook = request.files.get("bank_passbook")

        upload_folder = os.path.join(
            "static",
            "uploads"
        )

        os.makedirs(upload_folder, exist_ok=True)

        def save_file(file):

            if file and file.filename:

                file_path = os.path.join(
                    upload_folder,
                    file.filename
                )

                file.save(file_path)

                return file.filename

            return ""

        aadhaar_name = save_file(aadhaar)
        income_name = save_file(income_certificate)
        caste_name = save_file(caste_certificate)
        marks_name = save_file(marks_memo)
        bank_name = save_file(bank_passbook)

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO documents
            (
                student_id,
                aadhaar,
                income_certificate,
                caste_certificate,
                marks_memo,
                bank_passbook
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            aadhaar_name,
            income_name,
            caste_name,
            marks_name,
            bank_name
        ))

        conn.commit()
        conn.close()

        return "Documents uploaded successfully."

    return render_template("documents.html")


# ---------------- APPLICATION ----------------

@app.route("/application", methods=["GET", "POST"])
def application():

    if request.method == "POST":

        student_id = request.form["student_id"]
        scholarship = request.form["scholarship"]
        academic_score = request.form["academic_score"]
        income = request.form["income"]
        category = request.form["category"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO applications
            (
                student_id,
                scholarship,
                academic_score,
                income,
                category,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            scholarship,
            academic_score,
            income,
            category,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("status"))

    return render_template("application.html")


# ---------------- APPLICATION STATUS ----------------

@app.route("/status")
def status():

    conn = get_db_connection()

    applications = conn.execute("""
        SELECT *
        FROM applications
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "status.html",
        applications=applications
    )


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":

    create_tables()

    app.run(debug=True)