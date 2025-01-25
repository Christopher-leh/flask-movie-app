from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FileField, SubmitField
from wtforms.validators import InputRequired

class MovieForm(FlaskForm):
    title = StringField("Titel", validators=[InputRequired()])
    description = TextAreaField("Beschreibung")
    release_year = IntegerField("Erscheinungsjahr")
    image = FileField("Filmcover hochladen")  # Bild-Upload
    submit = SubmitField("Film hinzufügen")

class ReviewForm(FlaskForm):
    rating = StringField("Bewertung (0.0 - 10.0)", validators=[InputRequired()])
    comment = TextAreaField("Kommentar")
    submit = SubmitField("Bewertung abgeben")
