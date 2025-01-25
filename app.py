from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Movie, Review  # Hier wird db importiert
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_bcrypt import Bcrypt
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from models import db, Movie
from forms import MovieForm, ReviewForm

from flask_migrate import Migrate
from models import db, Movie  # Stelle sicher, dass das importiert ist



app = Flask(__name__)

# Verbindung zur Datenbank (PostgreSQL von Render oder fallback zu SQLite)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("❌ Fehler: DATABASE_URL ist nicht gesetzt! Stelle sicher, dass die PostgreSQL-Datenbank verbunden ist.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supergeheimeschluessel123")



db.init_app(app)  # Datenbank mit Flask-App verbinden


bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class RegisterForm(FlaskForm):
    username = StringField("Benutzername", validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField("Passwort", validators=[InputRequired()])
    submit = SubmitField("Registrieren")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))  # Nach Registrierung zum Login
    return render_template('register.html', form=form)


class LoginForm(FlaskForm):
    username = StringField("Benutzername", validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField("Passwort", validators=[InputRequired()])
    submit = SubmitField("Anmelden")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))  # Nach dem Login zur Startseite
    return render_template('login.html', form=form)



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Stellt sicher, dass Nutzer geladen wird

#@app.route('/')
#def index():
#    movies = Movie.query.all()
#    for movie in movies:
#        reviews = Review.query.filter_by(movie_id=movie.id).all()
#        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
#        movie.avg_rating = avg_rating  # Dynamisches Attribut hinzufügen

    return render_template('index.html', movies=movies)

@app.route('/')
def index():
    all_movies = Movie.query.all()

    # Watchlist: Alle Filme ohne Bewertung des aktuellen Nutzers
    watchlist_movies = [movie for movie in all_movies if not Review.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()]

    # Bereits gesehen: Alle Filme mit einer Bewertung des aktuellen Nutzers
    gesehen_movies = [movie for movie in all_movies if Review.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()]

    # Beste Filme: Alle Filme, die mindestens eine Bewertung haben
    best_movies = Movie.query.join(Review).group_by(Movie.id).all()

    # Durchschnittliche Bewertung berechnen
    for movie in best_movies:
        reviews = Review.query.filter_by(movie_id=movie.id).all()
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
        movie.avg_rating = avg_rating

    # Filme nach Bewertung absteigend sortieren
    best_movies = sorted(best_movies, key=lambda x: x.avg_rating or 0, reverse=True)

    return render_template('index.html', watchlist=watchlist_movies, gesehen=gesehen_movies, bestenliste=best_movies)



@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = ReviewForm()  # Formular für Bewertungen erstellen
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    return render_template('movie.html', movie=movie, form=form, reviews=reviews)




UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = None  # Standardwert setzen
        
        if file and allowed_file(file.filename):  # Prüfen, ob Datei erlaubt ist
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Bild speichern
            
        # Neuen Film mit oder ohne Bild zur Datenbank hinzufügen
        new_movie = Movie(
            title=form.title.data,
            description=form.description.data,
            release_year=form.release_year.data,
            image_filename=filename, # Falls kein Bild hochgeladen wird, bleibt None
           added_by_id=current_user.id # 🆕 Speichert die ID des eingeloggten Nutzers
        )
        
        db.session.add(new_movie)
        db.session.commit()
        
        flash("Film erfolgreich hinzugefügt!", "success")
        return redirect(url_for('index'))
    
    return render_template('add_movie.html', form=form)



@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # 🟢 Überprüfen, ob der Benutzer "Chris" ist oder den Film hinzugefügt hat
    if current_user.username != "Chris" and movie.added_by_id != current_user.id:
        flash("❌ Du kannst nur Filme löschen, die du hinzugefügt hast oder wenn du Admin bist!", "danger")
        return redirect(url_for('index'))

    # Falls der Film ein Bild hat, dieses aus dem Upload-Ordner löschen
    if movie.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], movie.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(movie)
    db.session.commit()

    flash("✅ Film wurde erfolgreich gelöscht!", "success")
    return redirect(url_for('index'))


@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)

    if form.validate_on_submit():
        movie.title = form.title.data
        movie.description = form.description.data
        movie.release_year = form.release_year.data

        # Prüfen, ob ein neues Bild hochgeladen wurde
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                movie.image_filename = filename  # Neues Bild speichern

        db.session.commit()
        flash("Film wurde erfolgreich aktualisiert!", "success")
        return redirect(url_for('movie_detail', movie_id=movie.id))

    return render_template('edit_movie.html', form=form, movie=movie)

@app.route('/movie/<int:movie_id>/review', methods=['POST'])
@login_required  # Nutzer muss eingeloggt sein
def add_review(movie_id):
    form = ReviewForm()
    movie = Movie.query.get_or_404(movie_id)

    if form.validate_on_submit():
        try:
            rating = float(form.rating.data)
            if 0.0 <= rating <= 10.0:  # Bewertung muss zwischen 0 und 10 sein
                review = Review(
                    user_id=current_user.id,  # Speichert die ID des eingeloggten Nutzers
                    movie_id=movie.id,
                    rating=rating,
                    comment=form.comment.data
                )
                db.session.add(review)
                db.session.commit()
                flash("Bewertung erfolgreich hinzugefügt!", "success")
            else:
                flash("Bewertung muss zwischen 0.0 und 10.0 liegen.", "danger")
        except ValueError:
            flash("Ungültige Bewertung! Bitte eine Zahl zwischen 0.0 und 10.0 eingeben.", "danger")

    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Überprüfung: Darf der Nutzer die Bewertung löschen?
    if review.user_id != current_user.id:
        flash("Du kannst nur deine eigenen Bewertungen löschen!", "danger")
        return redirect(url_for('movie_detail', movie_id=review.movie_id))

    db.session.delete(review)
    db.session.commit()
    flash("Bewertung gelöscht!", "success")
    return redirect(url_for('movie_detail', movie_id=review.movie_id))

@app.route('/my_movies')
@login_required
def my_movies():
    # Filme, die der Nutzer hinzugefügt hat
    added_movies = Movie.query.filter_by(added_by_id=current_user.id).all()

    # Filme, die der Nutzer bewertet hat (distinct, um doppelte Filme zu vermeiden)
    reviewed_movies = (
        Movie.query.join(Review).filter(Review.user_id == current_user.id).distinct().all()
    )

    # Filme zusammenführen, dabei doppelte Einträge entfernen
    all_my_movies = list({movie.id: movie for movie in added_movies + reviewed_movies}.values())

    return render_template('my_movies.html', movies=all_my_movies)


@app.route('/rated_movies')
def rated_movies():
    rated_movies = (
        Movie.query
        .join(Review)
        .group_by(Movie.id)
        .order_by(db.func.avg(Review.rating).desc())  # Sortiert nach Bewertung
        .all()
    )

    # Durchschnittliche Bewertung berechnen
    for movie in rated_movies:
        reviews = Review.query.filter_by(movie_id=movie.id).all()
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
        movie.avg_rating = avg_rating

    return render_template('rated_movies.html', rated_movies=rated_movies)



@app.route('/all_movies')
def all_movies():
    movies = Movie.query.all()  # Alle Filme abrufen
    return render_template('all_movies.html', movies=movies)

@app.route('/watched_movies')
@login_required
def watched_movies():
    watched_movies = (
        Movie.query
        .join(Review)
        .filter(Review.user_id == current_user.id)
        .group_by(Movie.id)
        .all()
    )

    # Durchschnittliche Bewertung berechnen
    for movie in watched_movies:
        reviews = Review.query.filter_by(movie_id=movie.id).all()
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
        movie.avg_rating = avg_rating

    return render_template('watched_movies.html', watched_movies=watched_movies)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/update-log')
def update_log():
    updates = [
        {"date": "25.01.2025", "time":"22:00 ", "changes": "Neue Liste: Meine Filme"},
        {"date": "25.01.2025", "time":"21:45 ", "changes": "Neue Listenunterteilung und Einzelansicht"},
        {"date": "25.01.2025", "time":"21:00 ", "changes": "Update log hinzugefügt"},
        {"date": "25.01.2025", "time":"20:40 ", "changes": "Design verbessert, mehr Abstand zwischen Listen"},
        {"date": "25.01.2025", "time": "20:00", "changes": "Filmliste und Bereits gesehen hinzugefügt"},
        {"date": "25.01.2025", "time": "19:30",  "changes": "Benutzer können nur eigene Filme löschen"},
    ]
    return render_template('update_log.html', updates=updates)



migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            db.session.commit()
            print("✅ Datenbanktabellen wurden erstellt oder aktualisiert!")
        except Exception as e:
            print(f"❌ Fehler bei der Datenbankerstellung: {e}")

    app.run(debug=True)
