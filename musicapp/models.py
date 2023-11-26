from datetime import datetime
from musicapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password_hash = db.Column(db.String(50), nullable = False)
    profile_image = db.Column(db.String(20), nullable = True, default = 'default_image.jpg')
    is_creator = db.Column(db.Boolean, default = False)
    is_flagged = db.Column(db.Boolean, default = False )
    playlists = db.relationship('Playlist', backref = 'user', lazy = True)
    interactions = db.relationship('Interactions', backref = 'user', lazy = True)


    def __repr__(self):
        return f'User {self.username}'
    

playlist_song = db.Table('playlist_song',
                         db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), nullable = False),
                         db.Column('song_id', db.Integer, db.ForeignKey('song.id'), nullable = False))


class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), unique = True, nullable = False)
    path = db.Column(db.String(100), unique =True, nullable = False)
    duration = db.Column(db.Time, nullable = True)
    lyrics = db.Column(db.Text, unique = True, nullable = True)
    genre = db.Column(db.Enum('Pop', 'Metal', 'Other'), nullable = False, default = 'Other')
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable = False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    uploaded_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    interactions = db.relationship('Interactions', backref = 'song', lazy = True)

    def __repr__(self):
        return f'Song {self.title}'
    

class Album(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    cover_image = db.Column(db.String(20), nullable = False, default = 'default_image.jpg')
    songs = db.relationship('Song', backref = 'album', lazy = True)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f'Album {self.name}'


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    profile_image = db.Column(db.String(20), nullable = False, default = 'default_image.jpg')
    songs = db.relationship('Song', backref = 'artist', lazy = True)
    albums = db.relationship('Album', backref = 'artist', lazy = True) 

    def __repr__(self):
        return f'Artist {self.name}'


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    songs = db.relationship('Song', secondary = playlist_song, backref = 'playlists')
    display_image = db.Column(db.String(20), nullable = False, default = 'default_image.jpg')
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f'Playlist {self.name}'
     

class Interactions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable = False)
    liked = db.Column(db.Boolean, default = False)
    rating = db.Column(db.Enum('0', '1', '2', '3', '4', '5'), nullable = False, default = '0')

    def __repr__(self):
        return f'Liked {self.liked}, Rating {self.rating}'
    