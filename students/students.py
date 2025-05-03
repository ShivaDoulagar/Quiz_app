from flask import Blueprint,render_template,request,redirect,url_for,session,flash,jsonify
import sqlite3
import datetime
from collections import Counter


students_bp = Blueprint("students", __name__, template_folder="templates", static_folder="static")



def user_name(mail):
    db = None
    try:
        if "user" not in session or session["user"]["role"] != "student":
            flash("Access denied! Please log in as a student.")
            return redirect(url_for("signin"))
        db = sqlite3.connect("instance/quiz_master.db")
        cur = db.cursor()
        name = cur.execute(
                """
                SELECT fullname FROM users WHERE  mail = ?
            """,
                (mail,),
            ).fetchone()
        return name
    except Exception as e:
        print(e)
    finally:
        if db is not None:
            db.close()

@students_bp.route("/<mail>", methods=["GET", "POST"])
def student_dashboard(mail):
    if request.method == "GET":
        if "user" not in session or session["user"]["role"] != "student":
            flash("Access denied! Please log in as a student.")
            return redirect(url_for("signin"))
        db = None
        try:
            db = sqlite3.connect("instance/quiz_master.db")
            cur = db.cursor()
            new_data = cur.execute("""
                SELECT  quiz.id,COUNT(questions.quiz_id),quiz.date_of_quiz,quiz.time_duration,chapters.chapter_name,subjects.subject_name,quiz.quiz_title
                                FROM quiz
                                LEFT JOIN questions ON quiz.id = questions.quiz_id
                                LEFT JOIN chapters ON chapters.id = questions.chapter_id
                                LEFT JOIN subjects on chapters.subject_id = subjects.id
                                GROUP BY quiz.id
            """).fetchall()
            name = user_name(mail) 
            return render_template(
                "home.html",
                new_data=new_data,
                mail=mail,
                date=str(datetime.date.today()),
                name=name[0],
                table=new_data,
                title = "Student-Dashboard"
            )

        except Exception as e:
            flash(f"An error occurred: {e}")
            print(f"Error: {e}")
            return redirect(url_for("signin"))

        finally:
            if db:
                db.close()
    else:
        db = None
        try:
            if "user" not in session or session["user"]["role"] != "student":
                flash("Access denied! Please log in as a student.")
                return redirect(url_for("signin"))
            quiz_id = request.args.get("quiz_id")
            db = sqlite3.connect("instance/quiz_master.db")
            cur = db.cursor()
            user_id = cur.execute(
                """
                        SELECT id
                        FROM users
                        WHERE mail = ?
            """,
                (mail,),
            ).fetchone()

            user = cur.execute(
                """
                SELECT user_id,quiz_id
                               FROM scores
                               WHERE user_id = ? AND quiz_id = ?
            """,
                (user_id[0], quiz_id),
            ).fetchone()
            print(user)
            if user:
                flash("Already attempted test!!!")
                return redirect(url_for("student_dashboard", mail=mail))
            return render_template("exam.html")
        except Exception as e:
            flash(f"Error:{str(e)}")
            return redirect(url_for("student_dashboard", mail=mail))
        finally:
            if db is not None:
                db.close()


@students_bp.route("<mail>/<int:quiz_id>", methods=["GET", "POST"])
def quiz_page(mail, quiz_id):
    if request.method == "GET":
        try:
            db = sqlite3.connect("instance/quiz_master.db")
            cur = db.cursor()
            quiz_data = cur.execute(
                """
                SELECT questions.question, questions.options, quiz.time_duration
                FROM questions
                JOIN quiz ON questions.quiz_id = quiz.id
                WHERE questions.quiz_id = ?
            """,
                (quiz_id,),
            ).fetchall()

            if not quiz_data:
                return jsonify({"error": "Quiz not found"}), 404
            time_duration = quiz_data[0][2].split(":")
            time = int(time_duration[0]) * 60 + int(time_duration[1])
            questions = [
                {"question": row[0], "options": eval(row[1])[:4]} for row in quiz_data
            ]
            return jsonify({"questions": questions, "time": time})

        except Exception as e:
            flash(f"Error:{e}")
        finally:
            if db is not None:
                db.close()

    elif request.method == "POST":
        db = None
        try:
            if "user" not in session or session["user"]["role"] != "student":
                flash("Access denied! Please log in as a student.")
                return redirect(url_for("signin"))
            db = sqlite3.connect("instance/quiz_master.db")
            cur = db.cursor()
            user = cur.execute('''
                SELECT scores.user_id,scores.quiz_id
                        FROM scores
                        JOIN users ON scores.user_id = users.id
                        WHERE users.id = ? AND scores.quiz_id = ? 
            ''',(mail,quiz_id)).fetchone()
            if user:
                flash("Already submited")
                return redirect(url_for('student_dashboard'))   
            answers = request.form
            given_answers = list(answers.values())
            answers = cur.execute(
                """
                SELECT questions.options
                FROM questions
                JOIN quiz ON questions.quiz_id = quiz.id
                WHERE questions.quiz_id = ?
            """,
                (quiz_id,),
            ).fetchall()
            ans = []
            li = []
            actual_li = []
            for x in answers:
                li.append(eval(x[0]))
            for x in li:
                ans.append(x[4])
            for x in li:
                actual_li.append(x[int(x[4]) - 1])
            score = 0
            for i in range(min(len(given_answers), len(actual_li))):
                if given_answers[i] == actual_li[i]:
                    score += 1

            user_id = cur.execute(
                """
                        SELECT id
                        FROM users
                        WHERE mail = ?
            """,
                (mail,),
            ).fetchone()
            cur.execute(
                """
    INSERT INTO scores (quiz_id, user_id,time, total_score,number_of_questions)
    VALUES (?, ?, ?,?,?)
""",
                (quiz_id, user_id[0], datetime.datetime.now(), score, len(actual_li)),
            )
            db.commit()
            flash(f"Submitted Successfully! your score is {score} ")
            return jsonify(
                {
                    "success": True,
                    "message": "Quiz submitted successfully!",
                    "score": score,
                }
            )

        except Exception as e:
            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
        finally:
            if db is not None:
                db.close()


@students_bp.route("/<mail>/scores")
def scores(mail):
    if "user" not in session or session["user"]["role"] != "student":
                flash("Access denied! Please log in as a student.")
                return redirect(url_for("signin"))
    try:
        db = sqlite3.connect("instance/quiz_master.db")
        cur = db.cursor()
        cur.execute(
            """
                SELECT scores.quiz_id,scores.total_score,number_of_questions,scores.time,quiz.quiz_title
                    FROM scores 
                    JOIN users on users.id  = scores.user_id
                    JOIN quiz on quiz.id = scores.quiz_id
                    WHERE users.mail = ? 
        """,
            (mail,),
        )
        data = cur.fetchall()
        name = user_name(mail)
        return render_template("scores.html", mail=mail, data=data,name = name[0],title = "Scores")
    except Exception as e:
        flash(f"Error:{e}")
        return redirect(url_for("student_dashboard", mail=mail))
    finally:
        if db is not None:
            db.close()


@students_bp.route("/<mail>/summary")
def summary(mail):
    if "user" not in session or session["user"]["role"] != "student":
                flash("Access denied! Please log in as a student.")
                return redirect(url_for("signin"))
    try:
        db = sqlite3.connect("instance/quiz_master.db")
        cur = db.cursor()
        cur.execute(
            """
                SELECT scores.quiz_id,scores.total_score,number_of_questions
                    FROM scores 
                    JOIN users on users.id  = scores.user_id
                    WHERE users.mail = ? 
        """,
            (mail,),
        )
        data = cur.fetchall()
        name = user_name(mail)
        return render_template("summary.html", mail=mail, data=data,name = name[0],title = "Summary")
    except Exception as e:
        flash(f"Error:{e}")
        return redirect(url_for("student_dashboard", mail=mail))
    finally:
        if db is not None:
            db.close()


@students_bp.route("/<mail>/summary/api")
def quiz_data(mail):
    if "user" not in session or session["user"]["role"] != "student":
                flash("Access denied! Please log in as a student.")
                return redirect(url_for("signin"))
    try:
        db = sqlite3.connect("instance/quiz_master.db")
        cur = db.cursor()
        cur.execute(
            """
            SELECT subjects.subject_name, COUNT(quiz.id)
            FROM subjects
            JOIN chapters ON chapters.subject_id = subjects.id
            JOIN quiz ON quiz.chapter_id = chapters.id
            JOIN scores ON scores.quiz_id = quiz.id
            JOIN users ON users.id = scores.user_id
            WHERE users.mail = ?
            GROUP BY subjects.id
        """,
            (mail,),
        )
        quiz_attempts = cur.fetchall()
        cur.execute(
            """
    SELECT scores.time 
    FROM scores 
    JOIN users ON users.id = scores.user_id
    WHERE users.mail = ?
""",(mail,),)
        quiz_month_attempts = cur.fetchall()
        dates = [
            datetime.datetime.strptime(ts[0], "%Y-%m-%d %H:%M:%S.%f").strftime("%B %Y")
            for ts in quiz_month_attempts
        ]

        month_counts = dict(Counter(dates))
        
        return jsonify({
            "subject_attempts": quiz_attempts,
            "monthly_attempts": month_counts
        })
    except Exception as e:
        flash(f"Error:{e}")
        return redirect(url_for("student_dashboard", mail=mail))
    finally:
        if db is not None:
            db.close()





@students_bp.route('/profile')
def profile():
    mail = request.args.get('mail')
    return f"mail is {mail}"