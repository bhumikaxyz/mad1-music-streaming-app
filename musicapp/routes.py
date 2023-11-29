import os
from musicapp import app, db
from flask import render_template, url_for, flash, redirect, request, abort
from musicapp.forms import RegistrationForm, LoginForm, AdminLoginForm, UpdateProfileForm, UploadForm, CreatePlaylistForm
from musicapp.models import User, Song, Playlist, Album, Artist, Interactions
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(name=form.name.data, username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(message=f'Account successfully created for {form.name.data}. You can now log in.', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
            # flash(f'Login successful. You are now logged in as {form.username.data}', 'success')
            # return redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful. Incorrect username or password.', 'danger')
    return render_template('login.html', title='Login', form=form)


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
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('index'))
    return render_template('admin_login.html', title='AdminLogin', form=form)


@app.route('/home')
@login_required
def home():
    return render_template('home.html', songs=Song.query.all())

@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()

    if request.method == 'GET':
            form.name.data = current_user.name
            form.username.data = current_user.username

    if form.validate_on_submit():
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

@app.route('/register_creator')
def register_creator():
    return render_template('register_creator.html')


@app.route('/upload_song', methods=['GET', 'POST'])
def upload_song():
    form = UploadForm()
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            song = Song(filename=filename)
            db.session.add(song)
            db.session.commit()
            return redirect(url_for('home'))

    # if form.validate_on_submit():
    #     flash(f'{form.title.data} has been uploaded successfully', 'success')
    #     return redirect(url_for('home'))
    
    return render_template('upload_song.html', form=form)





@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/admin_options')
def admin_options():
    return render_template('admin_options.html')


@app.route('/creator_dashboard')
def creator_dashboard():
    return render_template('creator_dashboard.html')



# ================================= Playlist CRUD ========================================

@app.route('/playlist')
def playlist():
    playlists = Playlist.query.all()
    return render_template('playlist.html', playlists = playlists)


@app.route('/playlist/create', methods = ['GET','POST'])
@login_required
def create_playlist():
    form = CreatePlaylistForm()
    songs = Song.query.all()
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


@app.route('/playlist/update/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def update_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    form = CreatePlaylistForm()
    form.name.data = playlist.name
    songs = Song.query.all()
    form.songs.choices = [(song.id, song.title) for song in songs]


    if playlist.user_id != current_user.id:
        abort(403)
    else:
        if request.method == 'POST' and form.validate_on_submit():
            selected_songs = form.songs.data
            playlist.songs = Song.query.filter(Song.id.in_(selected_songs)).all()
            db.session.add(playlist)
            db.session.commit()
            flash('Your playlist has been created', 'success')
            return redirect(url_for('playlist'))
        
    return render_template('create_playlist.html', form=form, songs=songs, playlist=playlist, legend='Update Post')

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


#====================================== Song CRUD ===========================================


@app.route('/play/<int:song_id>')
def play_song(song_id):
    song = Song.query.get_or_404(song_id)
    try:
        lyrics = f"D:\Study Resources\IITM OD\mad1_project\musicapp\static\lyrics\{song.title}.txt"
        with open(lyrics, 'r') as file:
            file_content = file.read()
    except:
        file_content = 'Lyrics not available.'        
    return render_template('play_song.html', song=song, file_content=file_content)