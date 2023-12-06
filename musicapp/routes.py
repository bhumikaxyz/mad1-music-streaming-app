import os
from musicapp import app, db
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy import func
from musicapp.forms import RegistrationForm, LoginForm, AdminLoginForm, UpdateProfileForm, SongForm, PlaylistForm, AlbumForm, RateSongForm, FilterForm
from musicapp.models import User, Song, Playlist, Album, Artist, Interactions, playlist_song
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from mutagen.mp3 import MP3



def get_audio_duration(file_path):
    try: 
       
        audio = MP3(file_path)
        duration_in_seconds = audio.info.length
        minutes, seconds = divmod(duration_in_seconds, 60)
        duration = f"{int(minutes):02}:{int(seconds):02}"
        return duration
    except:
        return None 
 
# ======================================== Registration and Login =========================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user: 
            if user.is_flagged:
                flash('You are disallowed from using this platform', 'danger')
                return redirect(url_for('index'))
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful. Incorrect username or password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method=='POST' and form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(name=form.name.data, username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(message=f'Account successfully created for {form.name.data}. You can now log in.', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
            flash(f'You are now logged in as {form.username.data}', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('index'))
    return render_template('admin_login.html', title='AdminLogin', form=form)


# ========================================== USER ====================================================

@app.route('/home', methods=['GET'])
@login_required
def home():
    form = FilterForm(request.args, csrf_enabled=False) # Initialize form with GET query params
    songs = Song.query.filter_by(is_flagged=False).order_by(Song.timestamp.desc())

    if request.method == 'GET': # Validate form manually
        filter_type = form.filter_type.data
        filter_value = form.filter_value.data
        app.logger.debug('filter_type', filter_type)
        app.logger.debug('filter_value', filter_value)

        if filter_value:
            if filter_type == 'artist':
                # songs = songs.filter(Song.artist.ilike(f"%{filter_value}%"))
                songs = songs.join(Artist).filter(Artist.name.ilike(f"%{filter_value}%"))
            elif filter_type == 'title':
                songs = songs.filter(Song.title.ilike(f"%{filter_value}%"))
            elif filter_type == 'rating':
                try:
                    rating = float(filter_value)
                    songs = songs.join(Interactions).group_by(Song.id).having(db.func.avg(Interactions.rating) == rating)
                except ValueError:
                    flash('Invalid rating value. Please enter a numeric value.', 'danger')
    app.logger.debug(f'filtered songs{songs.all()}')
    return render_template('home.html', songs=songs.all(), form=form)

    


@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()

    if request.method == 'GET':
            form.name.data = current_user.name
            form.username.data = current_user.username

    if request.method == 'POST' and form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.name = form.name.data
            current_user.username = form.username.data
            hashed_password = generate_password_hash(form.password.data)
            current_user.password_hash = hashed_password
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('home'))
        else:  
            flash('Incorrect password', 'danger')  
            return redirect(url_for('profile'))
            
        
    return render_template('profile.html', form=form)  


@app.route('/register_creator', methods = ['GET', 'POST'])
@login_required
def register_creator():
    user = User.query.get_or_404(current_user.id)
    if request.method == 'POST' and not user.is_creator:
        user.is_creator = True
        db.session.commit()  
        flash('Account successfully upgraded to creator!', 'success')
        return redirect(url_for('home'))  
        
    return render_template('register_creator.html')

# ========================================= ADMIN ====================================================

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    songs = Song.query.all()
    creators = User.query.filter_by(is_creator=True).all()

    n_users = User.query.filter(User.is_creator==False).count()
    n_creators = User.query.filter(User.is_creator==True).count()
    n_songs = Song.query.count()
    n_albums = Album.query.count()
    n_artists = Artist.query.count()
    avg_rating = db.session.query(func.avg(Interactions.rating)).scalar()
    avg_rating = round(avg_rating, 1)


    return render_template('admin_dashboard.html', songs=songs, creators=creators,
                           n_users=n_users, n_creators=n_creators, n_songs=n_songs,
                           n_albums=n_albums, n_artists=n_artists, avg_rating=avg_rating)

@app.route('/blacklist_song/<int:song_id>', methods=['GET', 'POST'])
def blacklist_song(song_id):
    song = Song.query.get_or_404(song_id)
    if request.method=='POST':
        if song:
            song.is_flagged = True
            db.session.commit()
    return redirect(url_for('admin_dashboard'))  


@app.route('/whitelist_song/<int:song_id>', methods=['GET', 'POST'])
def whitelist_song(song_id):
    song = Song.query.get_or_404(song_id)
    if request.method=='POST':
        if song:
            song.is_flagged = False
            db.session.commit()
    return redirect(url_for('admin_dashboard'))  


@app.route('/blacklist_creator/<int:creator_id>', methods=['GET', 'POST'])
def blacklist_creator(creator_id):
    creator = User.query.get_or_404(creator_id)
    if request.method=='POST':
        if creator:
            creator.is_flagged = True
            db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/whitelist_creator/<int:creator_id>', methods=['GET', 'POST'])
def whitelist_creator(creator_id):
    creator = User.query.get_or_404(creator_id)
    if request.method=='POST':
        if creator:
            creator.is_flagged = False
            db.session.commit()
    return redirect(url_for('admin_dashboard'))


# ================================= CRUD on Playlists ========================================

@app.route('/playlist')
@login_required
def playlist():
    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.timestamp.desc()).all()
    return render_template('playlist.html', playlists = playlists)


@app.route('/playlist/create', methods = ['GET','POST'])
@login_required
def create_playlist():
    form = PlaylistForm()
    songs = Song.query.filter_by(is_flagged=False).all()
    form.songs.choices = [(song.id, song.title) for song in songs]
    
    if request.method == 'POST' and form.validate_on_submit():
        playlist = Playlist(name = form.name.data)
        playlist.user_id = current_user.id
        selected_songs = form.songs.data
        playlist.songs = Song.query.filter(Song.id.in_(selected_songs)).all()
        db.session.add(playlist)
        db.session.commit()
        flash('Your playlist has been created', 'success')
        return redirect(url_for('playlist'))
    return render_template('create_playlist.html', form=form, songs=songs, legend='Create a Playlist')


@app.route('/playlist/view/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = (
        db.session.query(Song)
        .join(playlist_song)
        .filter(Playlist.id == playlist_id, Song.is_flagged.is_(False))
        .all()
    )
    return render_template('view_playlist.html', playlist=playlist, songs=songs)


@app.route('/playlist/update/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def update_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    form = PlaylistForm()
    songs = Song.query.filter_by(is_flagged=False).all()
    form.songs.choices = [(song.id, song.title) for song in songs]
    existing_songs=[song.id for song in playlist.songs]
    
    if request.method=='GET':
        form.name.data = playlist.name
        
    if playlist.user_id != current_user.id:
        abort(403)
    else:
        if request.method == 'POST' and form.validate_on_submit():
            playlist.name = form.name.data
            selected_songs = form.songs.data
            playlist.songs = Song.query.filter(Song.id.in_(selected_songs)).all()
            db.session.add(playlist)
            db.session.commit()
            flash('Your playlist has been updated.', 'success')
            return redirect(url_for('playlist'))
        
    return render_template('create_playlist.html', form=form, songs=songs, playlist=playlist, legend='Update Post', existing_songs=existing_songs)

@app.route('/playlist/delete/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        abort(403)
    db.session.delete(playlist)
    db.session.commit()
    flash('Your playlist has been deleted', 'success')
    return redirect(url_for('playlist'))


#======================================== CRUD on Albums ============================================

@app.route('/creator_dashboard')
@login_required
def creator_dashboard():
    albums = Album.query.filter_by(creator_id=current_user.id).order_by(Album.timestamp.desc()).all()
    n_songs = Song.query.filter(Song.creator_id==current_user.id).count()
    n_albums = Album.query.filter(Album.creator_id==current_user.id).count()
    avg_rating = (
    db.session.query(func.avg(Interactions.rating))
    .join(Song)
    .filter(Song.creator_id == current_user.id)
    .scalar()
    )
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating=0    

    return render_template('creator_dashboard.html', albums=albums, n_songs=n_songs, n_albums=n_albums, avg_rating=avg_rating)


@app.route('/album/create', methods=['GET', 'POST'])
@login_required
def create_album():
    form = AlbumForm()
    songs = Song.query.filter_by(is_flagged=False, creator_id=current_user.id).all()
    form.songs.choices = [(song.id, song.title) for song in songs]

    if request.method == 'POST' and form.validate_on_submit():
        album = Album(name=form.name.data)
        album.creator_id = current_user.id
        artist = Artist.query.filter(Artist.name==form.artist.data).first()
        if not artist:
            artist = Artist(name=form.artist.data)
            db.session.add(artist)
            db.session.commit()

        album.artist_id=artist.id
        album.genre = form.genre.data
        selected_songs = form.songs.data
        query_songs = Song.query.filter(Song.id.in_(selected_songs))
        album.songs = list(query_songs)
        for song in album.songs:
            song.artist_id = artist.id
            db.session.add(song)
        db.session.add(album)
        db.session.commit()
        flash(f'Album {album.name} has been created', 'success')
        return redirect(url_for('creator_dashboard'))

    return render_template('create_album.html', form=form, songs=songs, legend='Create an Album')


@app.route('/album/view/<int:album_id>', methods=['GET', 'POST'])
@login_required
def view_album(album_id):
    album = Album.query.get_or_404(album_id)
    songs = album.songs
    return render_template('view_album.html', album=album, songs=songs)


@app.route('/album/update/<int:album_id>', methods=['GET', 'POST'])
@login_required
def update_album(album_id):
    album = Album.query.get_or_404(album_id)
    form = AlbumForm()
    # form.artist.data = album.artist
    songs = Song.query.filter_by(is_flagged=False, artist_id=album.artist_id, creator_id=current_user.id).all()
    existing_songs=[song.id for song in album.songs]
    form.songs.choices = [(song.id, song.title) for song in songs]

    if request.method == 'GET':
        form.name.data = album.name
        form.genre.data = album.genre
    
    if request.method == 'POST' and form.validate_on_submit():
        # artist_name = form.artist.data
        # artist = Artist.query.filter_by(name=artist_name).first()
        # if not artist:
        #     artist = Artist(name=form.artist.data)
        #     db.session.add(artist)
        #     db.session.commit()

         # album.artist_id=artist.id
        album.name = form.name.data
        album.genre = form.genre.data
        selected_songs = form.songs.data
        query_songs = Song.query.filter(Song.id.in_(selected_songs)).all()
        album.songs = list(query_songs)
        db.session.add(album)
        db.session.commit()
        flash(f'Album {album.name} has been updated', 'success')
        return redirect(url_for('creator_dashboard'))
        
    return render_template('update_album.html', form=form, songs=songs, existing_songs=existing_songs, album=album, legend='Update Album')


@app.route('/album/delete/<int:album_id>', methods=['GET', 'POST'])
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    flash('Album has been deleted', 'success')
    return redirect(url_for('creator_dashboard'))
   
    

#====================================== CRUD on Songs ===================================================


@app.route('/play/<int:song_id>', methods=['GET', 'POST'])
def play_song(song_id):
    song = Song.query.get_or_404(song_id)
    form = RateSongForm()

    if song.lyrics:
        lyrics = song.lyrics
    else:    
        try:
            filepath = f"D:\Study Resources\IITM OD\mad1_project\musicapp\static\lyrics\{song.title}.txt"
            with open(filepath, 'r') as file:
                lyrics = file.read()
        except:
            lyrics = 'Lyrics not available.'      
    return render_template('play_song.html', song=song, lyrics=lyrics, form=form)


@app.route('/create_song', methods=['GET', 'POST'])
def create_song():
    form = SongForm()

    if request.method=='POST':
        file = request.files['file']
        app.logger.debug('file found')
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        artist = Artist.query.filter(Artist.name==form.artist.data).first()
        if not artist:
            artist = Artist(name=form.artist.data)
            db.session.add(artist)
            db.session.commit()

        song = Song(filename=filename)
        song.creator_id = current_user.id
        song.title = form.title.data
        song.artist_id = artist.id
        song.lyrics = form.lyrics.data
        duration = get_audio_duration(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        song.duration = duration
        db.session.add(song)
        db.session.commit()

        flash(f'{form.title.data} has been uploaded successfully', 'success')
        return redirect(url_for('home'))

    return render_template('create_song.html', form=form, legend='Upload a Song')


@app.route('/song/update/<int:song_id>', methods=['GET', 'POST'])
@login_required
def update_song(song_id):
    song = Song.query.get_or_404(song_id)
    form = SongForm()
    if request.method=='GET':
        form.title.data = song.title
        form.artist.data = song.artist
        form.lyrics.data = song.lyrics

    if request.method == 'POST' and form.validate_on_submit():

        artist_name = form.artist.data
        artist = Artist.query.filter_by(name=artist_name).first()

        if not artist:
            artist = Artist(name=artist_name)
            db.session.add(artist)
            db.session.commit()

        song.title = form.title.data
        song.artist_id = artist.id
        song.lyrics = form.lyrics.data
        db.session.commit()
        flash('Song has been updated', 'success')
        return redirect(url_for('home'))
        
    return render_template('update_song.html', form=form, legend='Update Song', song=song)



@app.route('/song/delete/<int:song_id>', methods=['GET', 'POST'])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.execute(playlist_song.delete().where(playlist_song.c.song_id == song_id))
    db.session.delete(song)
    db.session.commit()
    flash('Song has been deleted', 'success')
    return redirect(url_for('home'))



# ===================================== Song INTERACTIONS ============================================


@app.route('/rate/<int:song_id>', methods=['GET', 'POST'])
def rate_song(song_id):
    song = Song.query.get_or_404(song_id)
    user = current_user
    form = RateSongForm()
    if request.method=='POST' and form.validate_on_submit():
        rating = form.rating.data
        like = form.like.data
        existing_interaction = Interactions.query.filter_by(user_id=user.id, song_id=song.id).first()
        if existing_interaction:
            existing_interaction.rating = rating
            existing_interaction.liked = like
        else:
            new_interaction = Interactions(user_id=user.id, song_id=song.id, rating=rating, liked=like)
            db.session.add(new_interaction)
        
        db.session.commit()

    return redirect(url_for('play_song', song=song, form=form, song_id=song.id))

