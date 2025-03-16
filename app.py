from flask import Flask, render_template, request, session, redirect, url_for, flash
from forms import Signin_form
from forms import Register_form
import sqlite3
from datetime import timedelta
from werkzeug.security import generate_password_hash,check_password_hash
from admin.admin import admin_bp
from students.students import students_bp


app = Flask(__name__)
app.register_blueprint(admin_bp,url_prefix = "/admin")
app.register_blueprint(students_bp,url_prefix = "/students")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SECRET_KEY'] = "quiz app made by me and very secure!!!!!"




@app.route('/', methods=['GET', 'POST'])
def signin():
    form = Signin_form()

    if request.method == "GET":
        return render_template('login.html', form=form)

    elif request.method == "POST":
        mail = form.mail.data
        password = form.password.data

        # Hardcoded admin credentials for testing
        if mail == 'admin@gmail.com' and password == 'adminadmin':
            session['user'] = {'role': 'admin', 'email': mail}
            return redirect(url_for('admin_dashboard'))

        db = None
        try:
            db = sqlite3.connect('instance/quiz_master.db')
            cur = db.cursor()

            # Fetch user details securely
            user_data = cur.execute('SELECT  mail, password FROM users WHERE mail = ?', (mail,)).fetchone()
            if user_data and check_password_hash(user_data[1], password):
                session['user'] = {'role': 'student', 'email': mail}
                return redirect(url_for('student_dashboard',mail = user_data[0]))
            else:
                flash("Invalid email or password!")
                return render_template('login.html', form=form)
        except Exception as e:
            return render_template('error.html', error_message=str(e))

        finally:
            if db is not None:
                db.close()



@app.route('/admin/')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash("Access denied! Please log in as admin.")
        return redirect(url_for('signin'))
    return render_template('admin_dashboard.html')





@app.route('/students/<mail>')
def student_dashboard(mail):
    if 'user' not in session or session['user']['role'] != 'student':
        flash("Access denied! Please log in as a student.")
        return redirect(url_for('signin'))
    return render_template('home.html',name = session['user']['email'].split('@')[0] )


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('signin'))





@app.before_request
def session_timeout():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)  # Set timeout duration




def adapt_date(date):
    return date.isoformat()

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    mail = None
    password = None
    full_name=None
    qualification=None
    dob=None
    form = Register_form()
    if form.validate_on_submit():
        db = None
        try:
            mail = form.mail.data
            password = form.password.data
            full_name = form.full_name.data
            qualification = form.qualification.data
            dob = form.dob.data
            dob = adapt_date(dob)
            password = generate_password_hash(password)
            db = sqlite3.connect('instance/quiz_master.db')
            cur = db.cursor()
            cur.execute(f'''
                SELECT mail FROM users
                        WHERE mail = "{mail}"
            ''')
            already = cur.fetchone()
            if already:
                flash('User Already Exists!!!')
                return render_template('register.html',form = form,mail = mail,password = password,full_name = full_name,qualification= qualification,dob = dob)
            else:
                cur.execute('''
                    INSERT INTO users(mail,password,fullname,qualification,dob)
                            VALUES(?,?,?,?,?)
                ''',(mail,password,full_name,qualification,dob))
                db.commit()
                form = Signin_form()
                flash('Registered Successfully!!!')
                return redirect(url_for('signin'))

        except Exception as e:
            return str(e)
        
        finally:
            if db is not None:
                db.close()
        
    return render_template('register.html',form = form,mail = mail,password = password,full_name = full_name,qualification= qualification,dob = dob)





if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)
