from musicapp import app, db
from flask import render_template, url_for, flash, redirect, request
from musicapp.forms import RegistrationForm, LoginForm, AdminLoginForm, UploadForm, CreatePlayListForm
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
        if form.username.data == 'admin' and form.password.data == 'admin123':
            flash(f'You are now logged in as {form.username.data}', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('index'))
    return render_template('admin_login.html', title='AdminLogin', form=form)


@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/register_creator')
def register_creator():
    return render_template('register_creator.html')

@app.route('/upload_song')
def upload_song():
    form = UploadForm()

    if form.validate_on_submit():
        flash(f'{form.title.data} has been uploaded successfully', 'success')
        return redirect(url_for('home'))
    
    return render_template('upload_song.html', form=form)


@app.route('/play_song')
def play_song():
    return render_template('play_song.html')

@app.route('/create_playlist')
def create_playlist():
    form = CreatePlayListForm()
    return render_template('create_playlist.html', form=form)
    
@app.route('/admin_options')
def admin_options():
    return render_template('admin_options.html')