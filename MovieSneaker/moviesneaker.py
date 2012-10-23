from flask import Flask, request, session, Response, render_template, json, abort
from redis import Redis, from_url as redis_from_url
from rq import Queue
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache

from datetime import datetime, timedelta
import dateutil
import os

import sneakercore
import showtimesparsing

### Some environment setup boilerplate

try:
    from . import app
except ValueError: # we're debugging
    app = Flask(__name__,static_folder="../static")
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

showtime_parse_queue = Queue('showtime_parse',connection=redis)

rp = redis.connection_pool.connection_kwargs
cache = Cache(app,config={'CACHE_TYPE':'redis',
                          'CACHE_REDIS_HOST':rp.get('host'),
                          'CACHE_REDIS_POST':rp.get('port'),
                          'CACHE_REDIS_PASSWORD':rp.get('password')})
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
    return app.response_class(json.dumps(payload,
                                         indent=None if request.is_xhr else 2,cls=cls), mimetype='application/json')


### This is where the fun happens

@app.route('/')
def index():
    zipcode = request.args.get('zipcode')
    # TODO: if we have a zipcode just render
    return render_template('index.html')

def get_venues(zipcode):
    return Venue.query.join(Venue.zipcodes).filter(Zipcode.zipcode==zipcode.strip()).all()


@app.route('/api/v1/venues', defaults={'venue':None,'output_chains':None})
@app.route('/api/v1/venues/<venue>',defaults={'output_chains':None})
@app.route('/api/v1/venues/<venue>/chains',defaults={'output_chains':True})
#@cache.cached(timeout=30)
def venues(venue,output_chains):
    if venue:
        current_showings = Showing.query.filter_by(venue=int(venue)).all()
        if not current_showings:
            abort(404)
        if output_chains:
            chain_length = int(request.args.get('length',2))
            if chain_length > 4:
                abort(403)
            chains = sneakercore.find_chains([(s,s.start,s.end) for s in current_showings],chain_length=chain_length)
            response = {'chain_length':chain_length,
                        'chains':chains}

        else:
            response = {'showings':current_showings}
    else:
        zipcode = request.args.get('zipcode')
        if zipcode:
            matching_venues = get_venues(zipcode)
            if not matching_venues:
                matching_venues = get_showtimes_parse(zipcode)

            response = { 'venues' : matching_venues }
        else:
            matching_venues = Venue.query.all()
            response = { 'venues' : matching_venues }

    return jsonify(response)

@app.route('/api/v1/movie/<movie_id>')
def movie(movie_id):
    return jsonify(Movie.query.filter_by(id=movie_id).one())

def get_showtimes_parse(zipcode,ignore_cache=False):
    zip_object = get_or_create(db.session,Zipcode,{'zipcode':zipcode})

    d = datetime.today()
    parse_key = 'showtimes:%s:%s'%(zipcode,'-'.join(str(i) for i in d.isocalendar()))
    parse = redis.get(parse_key)
    if parse and not ignore_cache:
        parse = json.loads(parse,cls=showtimesparsing.ParseDecoder)
    else:
        parse = showtimesparsing.parse_from_flixster(zipcode,date=d)
        redis.set(parse_key,json.dumps(parse,cls=showtimesparsing.ParseEncoder))

    for theatre in parse['theatres']:
        venue = get_or_create(db.session,Venue,keys={'name':theatre['name']},additions={'address':theatre['address']},collections={'zipcodes':zip_object})
        for movie in theatre['movies']:
            movie_obj = get_or_create(db.session,Movie,{'name':movie['name']},additions={'runtime':movie['duration']})
            for showtime in movie['showtimes']:
                showing = get_or_create(db.session,Showing,{'movie':movie_obj.id,'venue':venue.id,'start':showtime['start'],'end':showtime['end']})
    db.session.commit()
    return get_venues(zipcode)


if DEBUG:
    @app.route('/fixtures')
    @cache.cached(timeout=15)
    def fixtures():
        if request.args.has_key('drop'):
            db.drop_all()
        db.create_all()

        ignore_cache = request.args.has_key('ignore_cache')

        zipcode = request.args.get('zipcode')
        if zipcode:
            response = {'venues':get_showtimes_parse(zipcode,ignore_cache)}
            return jsonify(response)

        else:
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