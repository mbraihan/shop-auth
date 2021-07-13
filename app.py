from functools import wraps
import json
# import psycopg2
# import requests
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode


import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
  load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = constants.SECRET_KEY


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated



# Controllers API
@app.route('/')
@requires_auth
def home():
    params = {
        'api_key': '{API_KEY}',
    }
    return render_template('home.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
@requires_auth
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))



@app.route('/products-training', methods=['GET'])
@requires_auth
def productsTraining():
    return render_template('productsTraining.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/new-station', methods=['GET'])
@requires_auth
def newStation():
    return render_template('newStation.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/my-account', methods=['GET'])
@requires_auth
def myAccount():
    return render_template('myAccount.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/add-camera', methods=['GET'])
@requires_auth
def addCamera():
    return render_template('addCamera.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/Camera-list', methods=['GET'])
@requires_auth
def addCamerat():
    return render_template('cameraList.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/Dataset-List', methods=['GET'])
@requires_auth
def dataSetList():
    return render_template('DatasetList.html',
    userinfo=session[constants.PROFILE_KEY],
    userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))



if __name__ == "__main__":
    app.run(debug = True)