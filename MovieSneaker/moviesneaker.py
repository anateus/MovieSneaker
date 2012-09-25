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

def venues_dict(vs):
    return [{'name':str(v.name)} for v in vs]

@app.route('/venues', defaults={'zipcode':None})
@app.route('/venues/', defaults={'zipcode':None})
@app.route('/venues/<zipcode>')
def venues(zipcode):
    if zipcode:
        matching_venues = venues_dict(Venue.query.join(Venue.zipcodes).filter(Zipcode.zipcode==zipcode.strip()).all())
    else:
        matching_venues = venues_dict(Venue.query.all())
#    if not matching_venues:
#        response = { 'error' }
    response = { 'venues' : matching_venues }
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)