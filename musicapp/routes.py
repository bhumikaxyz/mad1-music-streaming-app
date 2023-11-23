from musicapp import app
from flask import render_template, url_for, flash, redirect
from musicapp.forms import RegistrationForm, LoginForm
from musicapp.models import User, Song


@app.route('/')
@app.route('/home')
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

@app.route('/user-home')
def userhome():
    return render_template('user-home.html')