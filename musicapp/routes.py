import os
from musicapp import app, db
from flask import render_template, url_for, flash, redirect, request, session
from musicapp.forms import RegistrationForm, LoginForm, AdminLoginForm, UpdateProfileForm, UploadForm, CreatePlayListForm
from musicapp.models import User, Song
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


@app.route('/play/<int:song_id>')
def play_song(song_id):
    song = Song.query.get_or_404(song_id)
    # try:
    # lyrics = url_for('static', filename='lyrics/' + song.title + '.txt')
    lyrics = f"D:\Study Resources\IITM OD\mad1_project\musicapp\static\lyrics\{song.title}.txt"
    with open(lyrics, 'r') as file:
        file_content = file.read()
    # except:
    #     file_content = 'Lyrics not available.'        
    return render_template('play_song.html', song=song, file_content=file_content)

@app.route('/create_playlist')
def create_playlist():
    form = CreatePlayListForm()
    return render_template('create_playlist.html', form=form)
    

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/admin_options')
def admin_options():
    return render_template('admin_options.html')


@app.route('/creator_dashboard')
def creator_dashboard():
    return render_template('creator_dashboard.html')