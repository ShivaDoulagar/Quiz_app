from db import db
from datetime import datetime


class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mail = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    fullname = db.Column(db.String(50), nullable=False)
    qualification = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Users(id={self.id}, mail={self.mail}, fullname={self.fullname})>"


class Subjects(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String(50), nullable=False)
    subject_description = db.Column(db.String(255), nullable=True)


class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_name = db.Column(db.String(50), nullable=False)
    chapter_description = db.Column(db.String(255), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    subject = db.relationship('Subjects', backref='chapters')


class Quiz(db.Model):
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    quiz_title = db.Column(db.String(50), nullable=False,default="Unnamed Quiz")
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    time_duration = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.String(255), nullable=True)

    chapter = db.relationship('Chapter', backref='quiz')


class Questions(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_title = db.Column(db.String(255), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    options = db.Column(db.String(255), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    quiz = db.relationship('Quiz', backref='questions')


class Scores(db.Model):
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)
    number_of_questions = db.Column(db.Integer, nullable=False)

    quiz = db.relationship('Quiz', backref='scores')
    user = db.relationship('Users', backref='scores')

# class Jntu_scores(db.Model):
#     __tablename__ = 'jntu_scores'
    
#     id = db.Column(db.Integer,primary_key=True,autoincrement=True)
#     st_name = db.Column(db.String(60),nullable=False)
#     st_roll_number = db.Column(db.String(60),nullable=False)
#     st_sem = db.column(db.Integer,nullable=False)
#     st_subject = db.column(db.String(60))
#     st_grade = db.column(db.String(5))
#     st_credit = db.Column(db.Interger)
