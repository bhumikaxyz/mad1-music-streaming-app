from datetime import datetime
from musicapp import db, login_manager
from flask_login import UserMixin
from sqlalchemy.sql import func 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password_hash = db.Column(db.String(50), nullable = False)
    is_creator = db.Column(db.Boolean, default = False)
    is_flagged = db.Column(db.Boolean, default = False)

    playlists = db.relationship('Playlist', backref = 'user', lazy = True)
    interactions = db.relationship('Interactions', backref = 'user', lazy = True)


    def __repr__(self):
        return f'User {self.username}'
    

playlist_song = db.Table('playlist_song',
                         db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
                         db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True))


class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), unique = True, nullable = False)
    filename = db.Column(db.String(100), unique =True)
    duration = db.Column(db.Time, nullable = True)
    lyrics = db.Column(db.Text)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable = False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    timestamp = db.Column(db.DateTime(), server_default=func.now())

    
    interactions = db.relationship('Interactions', backref = 'song', lazy = True)

    def __repr__(self):
        return f'{self.title}'
    

class Album(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    genre = db.Column(db.String(100), nullable = True, default = 'Other')
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    timestamp = db.Column(db.DateTime, server_default=func.now())

    songs = db.relationship('Song', backref = 'album', lazy = True)
    
    def __repr__(self):
        return f'Album {self.name}'


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)

    songs = db.relationship('Song', backref = 'artist', lazy = True)
    albums = db.relationship('Album', backref = 'artist', lazy = True) 

    def __repr__(self):
        return f'{self.name}'


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    songs = db.relationship('Song', secondary = playlist_song, backref = 'playlists')
    timestamp = db.Column(db.DateTime, server_default=func.now())
    

    def __repr__(self):
        return f'Playlist {self.name}'
     

class Interactions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable = False)
    liked = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, nullable = False, default=0)

    def __repr__(self):
        return f'Liked {self.liked}, Rating {self.rating}'
    