from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from TubeSage.models import User
from flask_login import login_user, logout_user, login_required
from TubeSage.__init__ import db


auth = Blueprint('auth', __name__) # create a Blueprint object that we name 'auth'


@auth.route('/login', methods=['GET', 'POST']) # define login page path
def login(): # define login page fucntion
    if request.method=='GET': # if the request is a GET we return the login page
        return render_template('login.html')
    else: # if the request is POST the we check if the user exist and with te right password
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(username=username).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash('Please sign up before!')
            return redirect(url_for('auth.signup'))
        elif not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
        elif user.status == 'pending':
            flash('Your account is pending. Please wait for the access grant.')
            return redirect(url_for('auth.login'))
        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('main.home'))


@auth.route('/signup', methods=['GET', 'POST'])# we define the sign up path
def signup(): # define the sign up function
    if request.method=='GET': # If the request is GET we return the sign up page and forms
        return render_template('signup.html')
    else: # if the request is POST, then we check if the email doesn't already exist and then we save data
        username = request.form.get('username')
        # name = request.form.get('name')
        password = request.form.get('password')
        cfmpassword = request.form.get('confirmedPassword')
        email = request.form.get('email')
        # if username == "" or password == "":
        #     flash('User id already exists')
        #     return redirect(url_for('auth.signup'))
        user = User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('User id already exists')
            return redirect(url_for('auth.signup'))
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='sha256'),
                        email=email, status='pending')
        # add the new user to the database
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('main.noti_for_signup'))


@auth.route('/logout') # define logout path
@login_required
def logout(): #define the logout function
    logout_user()
    return redirect(url_for('main.home'))
