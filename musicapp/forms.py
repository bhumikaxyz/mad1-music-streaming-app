from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField, FileField, TimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Login')    
    

class UploadForm(FlaskForm):
    title = StringField('Song Title', validators=[DataRequired()])
    path = StringField('File Path', validators=[DataRequired()])
    duration = TimeField('Duration')
    genre = SelectField('Genre', default='Other')
    lyrics = TextAreaField('Lyrics')
    submit = SubmitField('Upload')

class CreatePlayListForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add Songs') 



