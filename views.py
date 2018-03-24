import boto3
import requests
import json
import matroid
from matroid.client import Matroid
from flask import request
from flask import render_template
from flask import Flask, abort, flash, redirect, render_template, request, url_for
#from flask.ext.stormpath import StormpathError, StormpathManager, User, login_required, login_user, logout_user, user
from flask import Flask, Response, redirect, url_for, request, session, abort
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user 
from app import app


# config
app.config.update(
    SECRET_KEY = 'yoyoma',
    LOGIN_DISABLED = False
)
# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20       
users = [User(id) for id in range(1, 21)]

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# @login_manager.unauthorized_handler
# def unauthorized_callback():
#     return redirect('http://www.google.com')


@app.route('/home')
@login_required
def home():
    api = Matroid(client_id = 'xRmlXjxOgAcbgYYq', client_secret = 'xwEdsDiE8Cx5XiBpGOsWrsRysVvkyfiy')
    logo_classification_result = api.classify_image(detector_id = '5ab6a975ae9d34000dce83fe', image_url = 'http://i.dailymail.co.uk/i/pix/2011/06/21/article-2006103-0CA8818400000578-744_1024x615_large.jpg')
    return str(logo_classification_result)

@app.route('/')
def index():
    return Response("Hello World12345!")

@app.route('/success')
def save_authentication():
    return render_template("success.html")

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(url_for('home'))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)