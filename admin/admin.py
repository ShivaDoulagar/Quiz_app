from flask import Blueprint,render_template, session, redirect, url_for, flash,request,jsonify
import sqlite3
import os
import ast

admin_bp = Blueprint("admin", __name__, static_folder='static', template_folder="templates")


@admin_bp.route('/addchapter', methods = ['POST'])
def add_chapter():
    db = None
    try:
        # Path to the database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()
        subject_name = request.form['subject_id']
        chapter_name = request.form['chapter_name']
        chapter_desc = request.form['chapter_description']
        cur.execute('''
                    INSERT INTO chapters(chapter_name,chapter_description,subject_id)
                        VALUES (?,?,?)
            ''',(chapter_name,chapter_desc,subject_name))
        db.commit()
        flash(f"Successfully added chapter: {chapter_name}")
        return redirect(url_for('admin_dashboard')) 
        
    except Exception as e:
        flash(f"Error: {e}")
        print(str(e))
        return redirect(url_for('admin.admin_dashboard'))
    finally:
        if db:
            db.close()
# modella
@admin_bp.route('/addSubject', methods=['POST'])
def add_subject():
    db = None
    try:
        name = request.form['name']
        description = request.form['description']

        
        # Path to the database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()
        
        # Insert into subjects table
        cur.execute('''
            INSERT INTO subjects (subject_name, subject_description)
            VALUES (?, ?)
        ''', (name, description))
        db.commit()
        
        flash(f"Successfully added subject: {name}")
        return redirect(url_for('admin_dashboard')) 

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('admin_dashboard')) 

    finally:
        if db is not None:
            db.close()

        

@admin_bp.route('/')
def list_of_subjects():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash("Access denied! Please log in as admin.")
        return redirect(url_for('signin'))

    try:
        db = sqlite3.connect('instance/quiz_master.db')
        cur = db.cursor()
        cur.execute('''
            SELECT 
                s.id AS subject_id, 
                s.subject_name, 
                s.subject_description,
                c.id AS chapter_id, 
                c.chapter_name, 
                c.chapter_description 
            FROM 
                subjects s
            LEFT JOIN 
                chapters c
            ON 
                s.id = c.subject_id
            ORDER BY s.id, c.id
        ''')
        data = cur.fetchall()

        # Organize data into a dictionary
        subjects = {}
        for row in data:
            subject_id, subject_name, subject_desc, chapter_id, chapter_name, chapter_desc = row
            if subject_id not in subjects:
                subjects[subject_id] = {
                    "subject_name": subject_name,
                    "subject_description": subject_desc,
                    "chapters": []
                }
            if chapter_id:
                subjects[subject_id]["chapters"].append({
                    "id":chapter_id,
                    "chapter_name": chapter_name,
                    "chapter_description": chapter_desc
                })

        return render_template("subjects.html", subjects=subjects)

    except Exception as e:
        flash(f"Something went wrong: {str(e)}")
        return redirect(url_for('signin'))
    finally:
        if db is not None:
            db.close()

@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()

        if request.method == 'POST':
            new_name = request.form['chapter_name']
            new_desc = request.form['chapter_description']

            # Update the chapter in the database
            cur.execute(
                "UPDATE chapters SET chapter_name = ?, chapter_description = ? WHERE id = ?",
                (new_name, new_desc, chapter_id),
            )
            db.commit()
            flash("Chapter updated successfully.")
            return redirect(url_for('admin_dashboard'))

        # Fetch the chapter details for pre-filling the form
        cur.execute("SELECT chapter_name, chapter_description FROM chapters WHERE id = ?", (chapter_id,))
        chapter = cur.fetchone()
        # return f"{chapter}"
        # Render the template with the chapter details
        return render_template('edit_chapter.html', chapter=chapter, chapter_id=chapter_id)

    except Exception as e:
        flash(f"Error: {e}")
        print(str(e))
        return redirect(url_for('admin.admin_dashboard'))  # Ensure valid return on error

    finally:
        if db:
            db.close()



@admin_bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()

        # Delete the chapter
        cur.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
        db.commit()

        flash("Chapter deleted successfully.")
    except Exception as e:
        flash(f"Error: {e}")
    finally:
        if db:
            db.close()

    return redirect(url_for('admin_dashboard'))

@admin_bp.route('/quiz')
def quiz():
    auth()
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()
        
        # Fetch all chapters
        chapters = cur.execute('''
            SELECT id, chapter_name
            FROM chapters
        ''').fetchall()

        # Fetch all quizzes
        quizs = cur.execute('''
            SELECT q.id, c.chapter_name, q.date_of_quiz, q.time_duration
            FROM quiz AS q
            JOIN chapters AS c ON c.id = q.chapter_id
        ''').fetchall()

        # Fetch all questions mapped to quizzes
        questions = cur.execute('''
            SELECT id, quiz_id, question_title
            FROM questions
        ''').fetchall()

        # Organize questions by quiz_id
        questions_by_quiz = {}
        for question in questions:
            quiz_id = question[1]
            if quiz_id not in questions_by_quiz:
                questions_by_quiz[quiz_id] = []
            questions_by_quiz[quiz_id].append((question[0], question[2]))  # (id, question_title)

        return render_template(
            "quiz.html",
            chapters=chapters,
            quizs=quizs,
            questions_by_quiz=questions_by_quiz  # Pass organized questions
        )

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('admin_dashboard'))
    finally:
        if db:
            db.close()




@admin_bp.route('/add_quiz',methods = ['GET','POST'])
def add_quiz():
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()

        chapter = request.form['chapter']
        chapter = ast.literal_eval(chapter)
        chapter = list(chapter)
        date = request.form['date']
        time = request.form['time']
        cur.execute('''
                INSERT INTO quiz(chapter_id,date_of_quiz,time_duration)
                    VALUES(?,?,?)
        ''',(chapter[0],date,time))
        db.commit()
        flash(f"Successfully added quiz: {chapter[1]}")
        return redirect(url_for('admin.quiz'))


    except Exception as e:
        flash(f"Error: {e}")
        return render_template(url_for("admin_dashboard"))
    finally:
        if db:
            db.close()



@admin_bp.route('/add_question/',methods = ['POST'])
def add_question():
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()

        id = request.form['quiz_id']
        chapter = request.form['chapter']
        chapter = ast.literal_eval(chapter)
        chapter = list(chapter)
        question_title = request.form['question_title']
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']
        li = [option1,option2,option3,option4,correct_option]
        li = str(li)
        cur.execute('''
                INSERT INTO questions(quiz_id,question_title,question,options,chapter_id)
                    VALUES (?,?,?,?,?)
        ''',(id,question_title,question,li,chapter[0]))
        db.commit()
        flash(f"Successfully added question {question_title} ")
        return redirect(url_for('admin.quiz'))
       
    except Exception as e:
        flash(f"Error:{e}")
    finally:
        if db:
            db.close()





@admin_bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    auth()  # Ensure user authentication
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()

        if request.method == 'POST':
            question_title = request.form['question_title']
            question = request.form['question']
            option1 = request.form['option1']
            option2 = request.form['option2']
            option3 = request.form['option3']
            option4 = request.form['option4']
            correct_option = request.form['correct_option']

            # Convert options to string format
            options = str([option1, option2, option3, option4, correct_option])

            # Update the question in the database
            cur.execute('''
                UPDATE questions
                SET question_title = ?, question = ?, options = ?
                WHERE id = ?
            ''', (question_title, question, options, question_id))

            db.commit()
            flash("Question updated successfully!")
            return redirect(url_for('admin.quiz'))

        # Fetch existing question data for GET request
        question_data = cur.execute('SELECT question_title, question, options FROM questions WHERE id = ?', (question_id,)).fetchone()
        
        if not question_data:
            flash("Question not found!")
            return redirect(url_for('admin.quiz'))

        # Convert stored options from string back to list
        options = eval(question_data[2]) if question_data[2] else [""] * 5  # Handle missing data
        
        return render_template("edit_question.html", question_id=question_id, question_title=question_data[0], question=question_data[1], options=options)

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('admin.quiz'))

    finally:
        if db:
            db.close()


@admin_bp.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    auth()
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor()

        # Delete the question
        cur.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        db.commit()
        
        flash("Question deleted successfully!")
        return redirect(url_for('admin.quiz'))

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('admin.quiz'))

    finally:
        if db:
            db.close()

@admin_bp.route('/summary')
def summary():
    return render_template('admin_summary.html')

@admin_bp.route('/summary/api')
def summary_api():
    db = None
    try:
        db = sqlite3.connect('instance/quiz_master.db')
        cur = db.cursor()
        cur.execute('''
                    SELECT s.subject_name, COALESCE(MAX(sc.total_score), 0) AS max_score
                    FROM subjects s
                    LEFT JOIN chapters c ON s.id = c.subject_id
                    LEFT JOIN quiz q ON c.id = q.chapter_id
                    LEFT JOIN scores sc ON q.id = sc.quiz_id
                    GROUP BY s.subject_name
        ''')
        top_scores = cur.fetchall()
        cur.execute('''
            SELECT strftime('%Y-%m', s.time) AS month, COUNT(s.id)
            FROM scores s
            GROUP BY month
        ''')
        attemps = cur.fetchall()
        data = {
            "top_scores": top_scores,
            "attemps": attemps
        }
        return jsonify(data)
    except Exception as e:
        flash(f"Error:{e}")
        return redirect(url_for("admin.quiz"))
    finally:
        if db is not None:
            db.close()




def auth():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash("Access denied! Please log in as admin.")
        return redirect(url_for('signin'))