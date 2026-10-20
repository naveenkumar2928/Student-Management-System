from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student_management_secret_key"

DATABASE = "database.db"

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            marks REAL NOT NULL,
            attendance REAL NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return redirect(url_for("login"))


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password")

    return render_template("login.html")


# Register page
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            flash("Registration successful. Please login.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already registered")

        finally:
            conn.close()

    return render_template("register.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    ai_students = conn.execute(
        "SELECT COUNT(*) FROM students WHERE department = 'AI'"
    ).fetchone()[0]

    it_students = conn.execute(
        "SELECT COUNT(*) FROM students WHERE department = 'IT'"
    ).fetchone()[0]

    ds_students = conn.execute(
        "SELECT COUNT(*) FROM students WHERE department = 'DS'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        ai_students=ai_students,
        it_students=it_students,
        ds_students=ds_students
    )


# Students page
@app.route("/students")
def students():

    search = request.args.get("search", "")
    department = request.args.get("department", "")
    year = request.args.get("year", "")

    conn = get_db_connection()

    query = "SELECT * FROM students WHERE 1=1"
    parameters = []

    if search:
        query += " AND (name LIKE ? OR email LIKE ?)"
        parameters.extend([
            "%" + search + "%",
            "%" + search + "%"
        ])

    if department:
        query += " AND department = ?"
        parameters.append(department)

    if year:
        query += " AND year = ?"
        parameters.append(year)

    query += " ORDER BY id DESC"

    students = conn.execute(
        query,
        parameters
    ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )


# Add student
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        year = request.form["year"]
        marks = request.form["marks"]
        attendance = request.form["attendance"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (name, email, department, year, marks, attendance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            department,
            year,
            marks,
            attendance
        ))

        conn.commit()
        conn.close()

        flash("Student added successfully")

        return redirect(url_for("students"))

    return render_template("add_student.html")


# Student details
@app.route("/student_details/<int:id>")
def student_details(id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        flash("Student not found")
        return redirect(url_for("students"))

    return render_template(
        "student_details.html",
        student=student
    )


# Edit student
@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if student is None:
        conn.close()
        flash("Student not found")
        return redirect(url_for("students"))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        year = request.form["year"]
        marks = request.form["marks"]
        attendance = request.form["attendance"]

        conn.execute("""
            UPDATE students
            SET name = ?,
                email = ?,
                department = ?,
                year = ?,
                marks = ?,
                attendance = ?
            WHERE id = ?
        """, (
            name,
            email,
            department,
            year,
            marks,
            attendance,
            id
        ))

        conn.commit()
        conn.close()

        flash("Student updated successfully")

        return redirect(url_for("students"))

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# Delete student
@app.route("/delete_student/<int:id>")
def delete_student(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully")

    return redirect(url_for("students"))


# Initialize database when the app starts
init_db()

# Run application locally
if __name__ == "__main__":
    app.run(debug=True)
