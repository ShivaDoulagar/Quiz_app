from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,EmailField,PasswordField,DateField
from wtforms.validators import DataRequired,Email,Length



class Signin_form(FlaskForm):
    mail = EmailField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired(),Length(6,20)])
    full_name = StringField("Full Name",validators=[DataRequired()])
    qualification = StringField("Qualification",validators=[DataRequired()])
    dob = DateField("Date Of Birth",validators=[DataRequired()])
    submit =  SubmitField("Login")