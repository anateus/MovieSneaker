from flask import Flask, request, session, Response, render_template, json
from redis import Redis, from_url as redis_from_url
from flask.ext.sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta

import os

### Some environment setup boilerplate

try:
    from . import app
except ValueError: # we're debugging
    app = Flask(__name__)
app.config.from_pyfile('moviesneaker.cfg')
db = SQLAlchemy(app)

from models import *

DEBUG = False
if os.path.exists('/home/dotcloud/environment.json'):
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
else: # we're debugging
    DEBUG = True
    env = None

if env:
    redis = redis_from_url(env["DOTCLOUD_DATA_REDIS_URL"])
else: # we're debugging
    redis = Redis()

### Various utilities I'll break out later

class SchemaEncoder(json.JSONEncoder):
    """
    Encodes JSON from SQLAlchemy schemas that have .__json__() as well as datetimes
    """
    def default(self, obj):
        if isinstance(obj, db.Model):
            return obj.__json__()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def jsonify(payload,cls=SchemaEncoder):
    """
    My replacement for flask's jsonify that uses a custom jsonencoder
    :param payload: The object to jsonify
    :type payload: Something serializable
    :param cls: A JSON encoder
    :type cls: JSONEncoder
    :return: The serialized json
    :rtype: str
    """
    return app.response_class(json.dumps(dict(payload),
                                         indent=None if request.is_xhr else 2,cls=cls), mimetype='application/json')


### This is where the fun happens

@app.route('/')
def index():
    return 'Even Gooder News Everyone!'


@app.route('/venues', defaults={'venue':None,'chains':None})
@app.route('/venues/<venue>',defaults={'chains':None})
@app.route('/venues/<venue>/chains',defaults={'chains':True})
def venues(venue,chains):
    if venue:
        current_showings = Showing.query.filter_by(venue=int(venue)).all()
        response = {'showings':current_showings}
        if chains:
            chain_length = int(request.args.get('length',2))
            # TODO: limit chain length
            response['chains']="chains of max length %d will go here"%chain_length
    else:
        zipcode = request.args.get('zipcode')
        if zipcode:
            matching_venues = Venue.query.join(Venue.zipcodes).filter(Zipcode.zipcode==zipcode.strip()).all()
            response = { 'venues' : matching_venues }
        else:
            matching_venues = Venue.query.all()
            response = { 'venues' : matching_venues }

    return jsonify(response)


if DEBUG:
    @app.route('/fixtures')
    def fixtures():
        if request.args.has_key('drop'):
            db.drop_all()
        db.create_all()
        v = None
        for i,z in enumerate(('94046','90210','02464'),start=1):
            zipcode = Zipcode(zipcode=z)
            db.session.add(zipcode)
            v = Venue('Theatre %s %d'%(z,i),[zipcode],description="Some movie theatre")
            db.session.add(v)

        m = Movie(name="Our one movie",runtime=90,description="Fantastic movie")
        db.session.add(m)
        db.session.commit()

        for i in range(10):
            st = datetime.now()+timedelta(minutes=20*i)
            en = st+timedelta(minutes=m.runtime)
            s = Showing(m,v,start=st,end=en)
            db.session.add(s)

        db.session.commit()

        return jsonify({"message":"seems to have worked!"})



if __name__ == '__main__':
    app.run(debug=True)