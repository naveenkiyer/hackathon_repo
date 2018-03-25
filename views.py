import boto3
import requests
import json
import matroid
import hashlib
import json
import os
import time
import requests
from matroid.client import Matroid
# from app import app
import urllib
from flask import Flask, abort, flash, redirect, render_template, request, url_for, jsonify
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

list_of_cameras = []
counter = 0
idx = 1
token = "c.mnDnhhSvAdqKkN6HA173o4y9khP8SQ08cgO1V4sO12wFLhhNRPgBkbuaGLcdANjvxyx0eFRUzAFeMCT3MXnntmc85qE8MMI55T0Eo8X9gNAJnEqHgg6k4JuZm7gl8s9w2ZbAz3hwY7ArHOpb" # Update with your token
device_id = 'aR3wCNI9AHsvHEmEGJAgdcptmAh2KIg0qmaWOGmBD5EdVEJOI5GYdg'

s3 = boto3.resource('s3', region_name='us-west-2')

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
        return render_template('home.html', list_of_cameras=list_of_cameras)
    # api = Matroid(client_id = 'xRmlXjxOgAcbgYYq', client_secret = 'xwEdsDiE8Cx5XiBpGOsWrsRysVvkyfiy')
    # logo_classification_result = api.classify_image(detector_id = '5ab6a975ae9d34000dce83fe', image_url = 'http://i.dailymail.co.uk/i/pix/2011/06/21/article-2006103-0CA8818400000578-744_1024x615_large.jpg')
    # return str(logo_classification_result)

@app.route('/authorize')
def authorize():
    return authorization_url

@app.route('/success')
def success():
    code = request.args.get('code')
    print(code)
    return(code)

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
            return render_template("home.html", list_of_cameras=list_of_cameras)

@app.route("/get_data")
def get_data():
    url = "https://developer-api.nest.com/"
    headers = {'Authorization': 'Bearer {0}'.format(token), 'Content-Type': 'application/json'} # Update with your token

    initial_response = requests.get(url, headers=headers, allow_redirects=False)
    if initial_response.status_code == 307:
        initial_response = requests.get(initial_response.headers['Location'], headers=headers, allow_redirects=False)

    #return initial_response.text
    json_data = json.loads(initial_response.text)
    url_source = json_data["devices"]["cameras"][device_id]["snapshot_url"]

    #urllib.urlretrieve(url_source, "test1.jpg")
    #ret_text = '<img style="-webkit-user-select: none; cursor; zoom-in;" src="' + url_source + '" width="810" height="456">'
    #return ret_text
    return '<iframe allowfullscreen webkitallowfullscreen mozallowfullscreen src="https://video.nest.com/embedded/live/zW42eZ201I" frameborder="0" width="720" height="576"></iframe>'
    #return '<iframe src="' + url_source + '" height="2000" width="2000"></iframe>'
# somewhere to logout

@app.route('/poll')
def poll():
    print("We are in poll!")
    global idx
    BUCKET_NAME = 'hackuva2018'
    target_fn = 'nav' + str(idx) + '.jpg'
    found = False
    for file in s3.Bucket('hackuva2018').objects.all():
        if target_fn == file.key:
            found = True
            print("We found a match for : " + target_fn)

    if found:
        idx += 1
        print("We have found this!")

    s3_link = 'https://s3-us-west-2.amazonaws.com/hackuva2018/' + target_fn
    ret = {'found':found, 'img_url':s3_link}
    print("ret is: " + str(ret))
    return jsonify(ret)

@app.route('/camera')
def camera():
    global idx

    cam_img = "https://s3-us-west-2.amazonaws.com/hackuva2018/nav" + str(idx) + ".jpg"
    return render_template("camera.html", cam_img=cam_img)

@app.route("/new_camera", methods=['GET', 'POST'])
def new_camera():
    # form = CameraForm(request.form)
 
    # # print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        list_of_numbers = request.form['list_of_numbers']

        print("IN NEW CAMERA")
        print(name)
        print(location)
        print(description)
        print(list_of_numbers)

        list_of_cameras.append({'name': name, 'location': location, 'description': description, list_of_numbers: 'list_of_numbers'})
        print(list_of_cameras)
        return render_template('home.html', list_of_cameras=list_of_cameras)
    else:
        return render_template('new_camera.html')



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