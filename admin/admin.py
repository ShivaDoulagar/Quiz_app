from flask import Blueprint,render_template, session, redirect, url_for, flash,request
import sqlite3
import os


admin_bp = Blueprint("admin", __name__, static_folder='static', template_folder="templates")




@admin_bp.route('/')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash("Access denied! Please log in as admin.")
        return redirect(url_for('signin'))  # Correct usage for main app routes
    return render_template('admin_dashboard.html')

@admin_bp.route('/addSubject', methods=['POST'])
def add_subject():
    db = None
    try:
        name = request.form['name']
        description = request.form['Discription']
        print(f"Name: {name}, Description: {description}")
        
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
        return redirect(url_for('admin.admin_dashboard'))  # Redirect to the admin dashboard

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('admin.admin_dashboard'))  # Redirect even on error

    finally:
        if db is not None:
            db.close()

        


@admin_bp.route('/list_sub')
def list_of_subjects():
    db = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'quiz_master.db')
        db = sqlite3.connect(db_path)
        cur = db.cursor() 

    except Exception :
        flash("Something went wrong try again later!")
        return redirect(url_for('admin.admin_dashboard'))