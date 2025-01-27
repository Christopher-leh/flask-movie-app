from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()  # Wichtige Initialisierung

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

#class Movie(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    title = db.Column(db.String(255), nullable=False)
#    description = db.Column(db.Text, nullable=True)
#    release_year = db.Column(db.Integer, nullable=True)
#    image_filename = db.Column(db.String(255), nullable=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,  db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)  # Nutzer-ID speichern
    movie_id = db.Column(db.Integer,  db.ForeignKey('movie.id', ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref='reviews')  # Nutzer-Objekt abrufen


class Movie(db.Model):
    __tablename__ = 'movie'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    #image_filename = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    # Beziehung zur Review-Tabelle
    reviews = db.relationship('Review', backref='movie', lazy=True)

     # Neues Feld: User, der den Film hinzugefügt hat
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    added_by = db.relationship('User', backref=db.backref('movies', lazy=True))


