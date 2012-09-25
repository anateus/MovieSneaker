from flask.ext.sqlalchemy import SQLAlchemy

from moviesneaker import app

db = SQLAlchemy(app)

zipcodes = db.Table('zipcodes',
                    db.Column('zipcode_id',db.Integer, db.ForeignKey('zipcode.id')),
                    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'))
)

class Zipcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.String(60), unique=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    runtime = db.Column(db.Integer) # in minutes
    description = db.Column(db.String(512))
    notes = db.Column(db.String(1024))
    showings = db.relationship('Showing')


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256)),
    address = db.Column(db.String(512)),
    description = db.Column(db.String(1024))
    # This isn't the actual zipcode this venue is in
    # Just the set of zipcodes this is considered close to
    zipcodes = db.relation('Zipcode', secondary=zipcodes, backref=db.backref('venues')) #models.ManyToManyField(ZipCode)
    showings = db.relationship('Showing')


class Showing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.Integer, db.ForeignKey('movie.id'))
    venue = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
