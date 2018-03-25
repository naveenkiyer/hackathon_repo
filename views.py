import boto3
import requests
import json
import matroid
from matroid.client import Matroid
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask import Response, request, session
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user 
from flask import json
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# UNCOMMENT ON AWS, if on dev server, run python views.py
app = Flask(__name__)

# config
app.config.update(
    SECRET_KEY = 'yoyoma',
)

cameras = {}

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')
    # api = Matroid(client_id = 'xRmlXjxOgAcbgYYq', client_secret = 'xwEdsDiE8Cx5XiBpGOsWrsRysVvkyfiy')
    # logo_classification_result = api.classify_image(detector_id = '5ab6a975ae9d34000dce83fe', image_url = 'http://i.dailymail.co.uk/i/pix/2011/06/21/article-2006103-0CA8818400000578-744_1024x615_large.jpg')
    # return str(logo_classification_result)

@app.route('/')
def index():
    return render_template('login.html')

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        print("HELLO")
        print(username)
        print(password)     
        if password == username + "_secret":
            # id = username.split('user')[1]
            # user = User(id)
            # login_user(user)
            # print("BEFORE REDIRECT")
            session['logged_in'] = True
            return home()
        else:
            flash('wrong password!')
            return abort(401)
    else:
        if session['logged_in'] == False:
            return render_template("login.html")
        else:
            return render_template("home.html")


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return render_template("login.html")
    
# callback to reload the user object        
def load_user(userid):
    return User(userid)

if __name__ == '__main__':
    app.run(debug=True)