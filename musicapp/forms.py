from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField, FileField, TimeField, SelectField, SelectMultipleField, ValidationError, widgets
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo
from musicapp.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken. Kindly choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Login')    
    

class UpdateProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('current_password')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken. Kindly choose a different one.')


class PlaylistForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    songs = SelectMultipleField('Songs', coerce=int, validators=[DataRequired()], widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    submit = SubmitField('Add Songs') 


class AlbumForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    genre = SelectField('Genre', choices=['Pop', 'Rock', 'Metal', 'Classical', 'Other'], validators=[DataRequired()])
    songs = SelectMultipleField('Songs', coerce=int, validators=[DataRequired()], widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    submit = SubmitField('Add Songs') 

class SongForm(FlaskForm):
    title = StringField('Song Title', validators=[DataRequired()])
    file = FileField('File', validators=[FileAllowed(['mp3'])])
    duration = TimeField('Duration')
    lyrics = TextAreaField('Lyrics')
    submit = SubmitField('Upload')


class RateSongForm(FlaskForm):
    rating = SelectField('Rate', choices=[1, 2, 3, 4, 5], validators=[DataRequired()])
    like = BooleanField('Like')
    submit = SubmitField('Submit')
    