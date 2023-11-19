from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

from forms import RegistrationForm, LoginForm

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(50), unique = True, nullable = False)
    password_hash = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(100), nullable = False)
    profile_image = db.Column(db.String(20), nullable = False, default = 'default_image.jpg')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    


    def __repr__(self):
        return f'User {self.username}'
    

class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), unique = True, nullable = False)
    lyrics = db.Column(db.Text, unique = True, nullable = True)
    duration = db.Column(db.String(10), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f'Song {self.title}'
    

class Album(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), unique = True, nullable = False)
    artist = db.Column(db.String(50), nullable = False)
    genre = db.Column(db.String(30), nullable = False)
    album_image = db.Column(db.String(20), nullable = False, default = 'default_image.jpg')




@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    form = RegistrationForm
    return render_template('register.html', title='', form=form)

@app.route('/login')
def login():
    form = LoginForm
    return render_template('login.html', title='', form=form)



if __name__ == '__main__':
    app.run(debug = True) 



