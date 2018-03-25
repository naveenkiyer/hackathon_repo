import boto3
import requests
import json
import matroid
import hashlib
import json
import requests
import os
import time
import requests
from matroid.client import Matroid
from app import app
from twilio.rest import Client
import urllib2
import urllib
from flask import Flask, abort, flash, redirect, render_template, request, url_for, jsonify
from flask import Response, request, session
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user 
from flask import json
# UNCOMMENT ON AWS, if on dev server, run python views.py
# app = Flask(__name__)

# config
app.config.update(
    SECRET_KEY = 'yoyoma',
)

counter = 0
idx = 1
token = "c.mnDnhhSvAdqKkN6HA173o4y9khP8SQ08cgO1V4sO12wFLhhNRPgBkbuaGLcdANjvxyx0eFRUzAFeMCT3MXnntmc85qE8MMI55T0Eo8X9gNAJnEqHgg6k4JuZm7gl8s9w2ZbAz3hwY7ArHOpb" # Update with your token
device_id = 'aR3wCNI9AHsvHEmEGJAgdcptmAh2KIg0qmaWOGmBD5EdVEJOI5GYdg'
api = Matroid(client_id = 'xRmlXjxOgAcbgYYq', client_secret = 'xwEdsDiE8Cx5XiBpGOsWrsRysVvkyfiy')
# Find these values at https://twilio.com/user/account
safetrek_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5FWTBPVVV3TVRSRU5qUTRSVUZDTkVJd01rUTBSVEUwUVRJMFF6ZzRSVGc1T0RBMFJEWXhOUSJ9.eyJodHRwOi8vY2xpZW50LW5hbWUiOiJIQUNLX1VWQSIsImlzcyI6Imh0dHBzOi8vbG9naW4tc2FuZGJveC5zYWZldHJlay5pby8iLCJzdWIiOiJzbXN8NWFiNzY3OTdhNjgwM2E5MTkxMWU4NTcxIiwiYXVkIjpbImh0dHBzOi8vYXBpLXNhbmRib3guc2FmZXRyZWsuaW8iLCJodHRwczovL3NhZmV0cmVrLXNhbmRib3guYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTUyMTk4NTQxMCwiZXhwIjoxNTIyMDIxNDEwLCJhenAiOiJtNXFYRjV6dE9kVDRjZFF0VWJaVDJnckJoRjE4N3Z3NiIsInNjb3BlIjoib3BlbmlkIHBob25lIG9mZmxpbmVfYWNjZXNzIn0.1HfW_wyqhp0Wak5eslxagIHLE1KK08HaxojzixDKGgDsWWo7zEvGw5wiuI54ewfsUVWy5ztPSoJE6offnXH6a3EuAsyAXqSeg3qpkuDZQEj5l8vdNEzUYE7yBaH9YTI_tuQ-fDEv7zwu5MOQWVmd8kVXDxiQXqyjFz3EapMfY_K-YPr3llu7bj7FtU3-o_ZXmGfdLNWs8KYKiQzE8DpODTqAc-r6htJb6K0ZbTzegJgzFR6EtOY9ckD0G8AVgwR_vvX6Pqnh6FrGlMrjRCZgEhilVqzjNNR_hDpFIfCaoswlUdPC81XohZlIujsyaK6raS3p10Ck6O6syHi7NRja1Q'
account_sid = "ACc34fdcbd4d14834b2a66185cc432e2a5"
auth_token = "9e0b428bf13c04b29296bed6defb0e73"
client = Client(account_sid, auth_token)
s3 = boto3.resource('s3', region_name='us-west-2')

called_API = False

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


@app.route('/test1')
def test1():
    return makeSafetrekCall()
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')

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
            return render_template("home.html")


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

@app.route('/safetrek')
def safetrek():

    return "We gotta authenticate this!"


def makeSafetrekCall():
    safetrek_url = "https://api-sandbox.safetrek.io/v1/alarms"
    payload = {
        'services': {
            'police': False,
            'fire': False,
            'medical': True
        },
        'location.coordinates': {
            'lat': 34.32334,
            'lng': -117.3343,
            'accuracy': 5
        }
    }

    headers = {'Authorization':'Bearer {0}'.format(safetrek_token),
               'Content-Type':'application/json'
                }

    r = requests.post(safetrek_url, data=json.dumps(payload), headers=headers)
    #print(r.content)
    print(r.content)
    return str(r.content)

@app.route('/poll')
def poll():
    print("We are in poll!")
    global idx
    global called_API
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

    fallen_prob = 0
    not_fallen_prob = 1

    if found:
        logo_classification_result = api.classify_image(detector_id = '5ab7a227471a8a000d92cef7', image_url = s3_link)
        #print(str(logo_classification_result))
        fallen_prob =  logo_classification_result['results'][0]['predictions'][0]['labels']['people laying down']
        not_fallen_prob = 1- fallen_prob

        if fallen_prob > 0.97:
            if !called_API:
                client.api.account.messages.create(
                        to="+17576797299",
                        from_="+17573798690",
                        body="Hi, it seems like user1 may have fallen down, we wanted you to check it out. You can see an"
                        + " image at: " + s3_link)

                makeSafetrekCall()
                called_API = True



    ret = {'found':found, 'img_url':s3_link, 'fallen':fallen_prob, 'not_fallen':not_fallen_prob}
    print("ret is: " + str(ret))
    return jsonify(ret)

@app.route('/camera')
def camera():
    global idx

    cam_img = "https://s3-us-west-2.amazonaws.com/hackuva2018/nav" + str(idx) + ".jpg"
    return render_template("camera.html", cam_img=cam_img)


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

# if __name__ == '__main__':
#     app.run(debug=True)