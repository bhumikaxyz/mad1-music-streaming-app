from musicapp import app
from flask import render_template, url_for, flash, redirect
from musicapp.forms import RegistrationForm, LoginForm, AdminLoginForm, UploadForm
from musicapp.models import User, Song


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'You are now logged in as {form.username.data}', 'success')
        return redirect(url_for('userhome'))
    return render_template('login.html', title='Login', form=form)


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