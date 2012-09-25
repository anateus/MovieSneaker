from flask.ext.sqlalchemy import SQLAlchemy
from flask import json

from moviesneaker import app

db = SQLAlchemy(app)

zipcodes = db.Table('zipcodes',
                    db.Column('zipcode_id',db.Integer, db.ForeignKey('zipcode.id')),
                    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'))
)

class Zipcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.String(60), unique=True)

    def __json__(self):
        return self.zipcode


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    runtime = db.Column(db.Integer) # in minutes
    description = db.Column(db.String(512))
    notes = db.Column(db.String(1024))
    showings = db.relationship('Showing')

    def __json__(self):
        return {'id':self.id,'name':self.name,'runtime':self.runtime,'description':self.description}


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    address = db.Column(db.String(512))
    description = db.Column(db.String(1024))
    # This isn't the actual zipcode this venue is in
    # Just the set of zipcodes this is considered close to
    zipcodes = db.relationship('Zipcode', secondary=zipcodes, backref=db.backref('venues')) #models.ManyToManyField(ZipCode)
    showings = db.relationship('Showing')

    def __init__(self,name,zipcodes,address=None,description=None,showings=None):
        self.name = name
        if isinstance(zipcodes,list):
            for zipcode in zipcodes:
                self.zipcodes.append(zipcode)
        # TODO: add sanitization of zipcode here
        elif isinstance(zipcodes,basestring):
            self.zipcodes.append(zipcodes)
        self.address = address
        self.description = description

        if isinstance(showings,list):
            for showing in showings:
                if isinstance(showing,Showing):
                    self.showings.append(showing)

    def __json__(self):
        return {'id':self.id,'name':str(self.name),'description':self.description,'zipcodes':self.zipcodes}

class Showing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.Integer, db.ForeignKey('movie.id'))
    venue = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __init__(self,movie,venue,start=None,end=None):
        # this allows passing in either the ids or the objects directly
        self.movie = movie.id if isinstance(movie, Movie) else movie
        print movie.id, isinstance(movie,Movie)
        self.venue = venue.id if isinstance(venue, Venue) else venue
        self.start = start
        self.end = end

    def __json__(self):
        return {'movie':Movie.query.filter_by(id=self.movie).one(),
                'venue':self.venue,
                'start':self.start,
                'end':self.end}




