from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

#----------- -----------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), default=[])
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String())
    shows = db.relationship('Show', backref='venue')

    @property
    def past_shows(self):
      return Show.query.filter(Show.venue_id == self.id, 
                              Show.start_time < func.now()).all()

    @property
    def past_shows_count(self):
      return Show.query.filter(Show.venue_id == self.id, 
                              Show.start_time < func.now()).count()

    @property
    def upcoming_shows(self):
      return Show.query.filter(Show.venue_id == self.id, 
                              Show.start_time > func.now()).all()

    @property
    def upcoming_shows_count(self):
      return Show.query.filter(Show.venue_id == self.id, 
                              Show.start_time > func.now()).count()

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), default=[])
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist')

    @property
    def past_shows(self):
      return Show.query.filter(Show.artist_id == self.id, 
                              Show.start_time < func.now()).all()

    @property
    def past_shows_count(self):
      return Show.query.filter(Show.artist_id == self.id, 
                              Show.start_time < func.now()).count()

    @property
    def upcoming_shows(self):
      return Show.query.filter(Show.artist_id == self.id, 
                              Show.start_time > func.now()).all()

    @property
    def upcoming_shows_count(self):
      return Show.query.filter(Show.artist_id == self.id, 
                              Show.start_time > func.now()).count()

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    @property
    def venue_name(self):
      return self.venue.name

    @property
    def artist_name(self):
      return self.artist.name

    @property
    def artist_image_link(self):
      return self.artist.image_link

    @property
    def venue_image_link(self):
      return self.venue.image_link