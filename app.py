from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123"  # Needed for session management


# ---------- DB INIT ----------
def init_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    # Teacher table
    cur.execute('''CREATE TABLE IF NOT EXISTS teacher
                   (firstname TEXT, email TEXT UNIQUE, password TEXT, subhandling TEXT)''')

    # Students table
    cur.execute('''CREATE TABLE IF NOT EXISTS students
                   (studentname TEXT,
                    classes TEXT,
                    marks INTEGER,
                    subject TEXT,
                    grade TEXT)''')

    con.commit()
    con.close()


# ---------- ROUTES ----------

@app.route("/")
def reg():
    return render_template("reg.html")


@app.route("/create")
def create():
    return render_template("newacc.html")


# Teacher register
@app.route("/acc", methods=['POST', 'GET'])
def acc():
    if request.method == 'POST':
        try:
            firstname = request.form['fname']
            email = request.form['email']
            password = request.form['pword']
            subject = request.form['sub']

            if firstname == "" or email == "" or password == "":
                flash("Please enter all the fields", "danger")
                return redirect(url_for("acc"))

            if len(password) < 6:
                flash("Password must be at least 6 characters", "danger")
                return redirect(url_for("acc"))

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute('INSERT INTO teacher(firstname, email, password, subhandling) VALUES (?, ?, ?, ?)',
                        (firstname, email, password, subject))
            con.commit()
            con.close()
            flash("Your details were successfully added", "success")
        except Exception as e:
            flash("Error in inserted values: " + str(e), "danger")
            return redirect(url_for("acc"))
        finally:
            return redirect(url_for("acc"))
    return render_template("newacc.html")


# Teacher login
@app.route("/submit", methods=['POST', 'GET'])
def submit():
    if request.method == "POST":
        name = request.form['first']
        email = request.form['em']
        password = request.form['p']

        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM teacher WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        con.close()

        if user:
            # save teacher's subject into session
            session['subject'] = user[3]  # subhandling
            session['teachername'] = user[0]  # firstname
            return render_template("welcome.html", names=name)
        else:
            flash("Invalid Email or Password", "danger")
            return render_template("reg.html")
@app.route("/back")
def back():
    return render_template("reg.html")
@app.route("/addstudent", methods=['POST', 'GET'])
def addstudent():
    if request.method == 'POST':
        try:
            studentname = request.form['stu']
            classs = request.form['cls']
            marks = request.form['marks']

            subject = session.get('subject')  # teacher's subject
            if not subject:
                flash("Please login first", "danger")
                return redirect(url_for("reg"))

            m = int(marks)
            if 90 <= m <= 100:
                grade = 'O'
            elif 80 <= m < 90:
                grade = 'A'
            elif 60 <= m < 80:
                grade = 'B'
            elif 45 <= m < 60:
                grade = 'C'
            elif 0 <= m < 45:
                grade = 'F'
            else:
                flash("Marks must be between 0 and 100", "danger")
                return redirect(url_for("addstudent"))

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute('INSERT INTO students(studentname, classes, marks, subject, grade) VALUES (?, ?, ?, ?, ?)',
                        (studentname, classs, marks, subject, grade))
            con.commit()
            con.close()
            flash("Student detail successfully added", "success")
            return redirect(url_for("addstudent"))
        except Exception as e:
            flash("Error in inserted values: " + str(e), "danger")
            return redirect(url_for("addstudent"))
    return render_template("student.html")
@app.route("/view")
def view():
    subject = session.get('subject')
    if not subject:
        flash("Please login first", "danger")
        return redirect(url_for("reg"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM students WHERE subject=?", (subject,))
    rows = cur.fetchall()
    con.close()
    return render_template("view.html", student=rows)
@app.route("/logout")
def logout():
    session.clear()
    return render_template("reg.html")
@app.route("/full")
def full():
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("SELECT * FROM students")
    rows=cur.fetchall()
    con.close()
    return render_template("fullview.html",student=rows)
if __name__ == '__main__':
    init_db()
    app.run(debug=True)