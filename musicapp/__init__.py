from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from musicapp.config import Config



app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from musicapp import routes
from musicapp.models import User, Song, Album, Artist, Playlist, Interactions




