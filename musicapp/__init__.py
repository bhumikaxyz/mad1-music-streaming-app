import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from musicapp.config import Config
from sqlalchemy.sql import func 


app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# with app.app_context():
#     db.create_all()
   

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from musicapp import routes
from musicapp.models import User, Song, Album, Artist, Playlist, Interactions




