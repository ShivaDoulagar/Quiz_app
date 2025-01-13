from flask import Blueprint,render_template,request,redirect,url_for,session,flash
import sqlite3


students_bp = Blueprint("students",__name__,static_folder='static',template_folder='templates')

@students_bp.route('/student')
def student_dashboard():
    if 'user' not in session or session['user']['role'] != 'student':
        flash("Access denied! Please log in as a student.")
        return redirect(url_for('signin'))
    return render_template('student_dashboard.html',name = session['user']['email'].split('@')[0] )


