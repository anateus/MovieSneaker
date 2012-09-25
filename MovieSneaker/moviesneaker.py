from flask import Flask, request, session, Response, render_template, json, jsonify
from redis import Redis, from_url as redis_from_url
from flask.ext.sqlalchemy import SQLAlchemy


import os

try:
    from . import app
except ValueError: # we're debugging
    app = Flask(__name__)
app.config.from_pyfile('moviesneaker.cfg')
db = SQLAlchemy(app)

from models import *

if os.path.exists('/home/dotcloud/environment.json'):
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
else: # we're debugging
    env = None

if env:
    redis = redis_from_url(env["DOTCLOUD_DATA_REDIS_URL"])
else: # we're debugging
    redis = Redis()

@app.route('/')
def index():
    return 'Even Gooder News Everyone!'

if __name__ == '__main__':
    app.run(debug=True)