#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.sql import func
import sys
import os
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------- -----------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), default=[])
    seeking_talent = db.Column(db.Boolean, default=True)
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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), default=[])
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=True)
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
    start_time = db.Column(db.DateTime)

    @property
    def venue_name(self):
      return Venue.query.get(self.venue_id).name

    @property
    def artist_name(self):
      return Artist.query.get(self.artist_id).name

    @property
    def artist_image_link(self):
      return Artist.query.get(self.artist_id).image_link

    @property
    def venue_image_link(self):
      return Venue.query.get(self.venue_id).image_link

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  places = db.session.query(Venue.city, Venue.state).distinct().all()
  for place in places:
    data.append({
      'city': place[0],
      'state': place[1],
      'venues': Venue.query.filter(Venue.city == place[0], Venue.state == place[1]).all()
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {}
  response['count'] = len(venues)
  response['data'] = venues

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={"csrf": False})
  
  venue = Venue()
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.image_link = form.image_link.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.website = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data

  error = False
  venue_id = None

  try:
    db.session.add(venue)
    db.session.commit()
    venue_id = venue.id
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.name + ' could not be listed.')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  error = False

  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was deleted successfully!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue with id' + venue_id + ' could not be deleted.')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  # TODO BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  if error:
    abort(500)
  else:
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = {}
  response['count'] = len(artists)
  response['data'] = artists

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  return render_template('pages/show_artist.html', artist=Artist.query.get(artist_id))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={"csrf": False})

  if not form.validate_on_submit():
    return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))

  artist = Artist.query.get(artist_id)

  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.image_link = form.image_link.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.website = form.website_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  
  error = False

  try:
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    flash(f'Some error occured. Artist {form.name.data} could not be saved!')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()

  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form, meta={"csrf": False})
  
  venue = Venue.query.get(venue_id)

  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.image_link = form.image_link.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.website = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data

  error = False

  try:
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    flash('Some error occured. Venue ' + form.name.data + ' could not be saved!')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form, meta={"csrf": False})

  if not form.validate_on_submit():
    return render_template('forms/new_artist.html', form=form)

  artist = Artist()

  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.image_link = form.image_link.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.website = form.website_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data

  error = False
  artist_id = None

  try:
    db.session.add(artist)
    db.session.commit()
    artist_id = artist.id
    flash(f'Artist {form.name.data} was successfully listed!')
  except:
    db.session.rollback()
    flash(f'Some error occured. Artist {form.name.data} could not be listed!')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm()

  show = Show()

  show.artist_id = form.artist_id.data
  show.venue_id = form.venue_id.data
  show.start_time = form.start_time.data

  error = True

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    error = False
  except:
    db.session.rollback()
    flash('An error occured. Show could not be listed!')
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('shows'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
