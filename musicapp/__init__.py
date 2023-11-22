from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from musicapp.config import Config
from musicapp.models import User, Song

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import musicapp.routes

