from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

TMDB_API_KEY = os.environ['TMDB_API_KEY']
TMDB_API_Bearer = os.environ['TMDB_API_Bearer']
TMDB_URL = 'https://api.themoviedb.org/3/search/movie'
TMDB_URL_MOVIE_DETAILS = 'https://api.themoviedb.org/3/movie'
TMDB_IMG_URL = 'https://image.tmdb.org/t/p/w500'
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_Bearer}"
}

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movies.db"
db = SQLAlchemy()
db.init_app(app)


class RateMovieForm(FlaskForm):
    rating = FloatField("Your rating out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class FindMovieForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add movie")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = i+1
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_movie_form = FindMovieForm()

    if add_movie_form.validate_on_submit():
        search_url = f"{TMDB_URL}?query={add_movie_form.movie_title.data}"
        response = requests.get(search_url, headers=headers)
        all_results = response.json()["results"]
        return render_template('select.html', movies=all_results)

    return render_template('add.html', form=add_movie_form)


@app.route("/select")
def select_movie():
    movie_id = request.args.get('id')
    search_url_movie_details = f"{TMDB_URL_MOVIE_DETAILS}/{movie_id}"
    response = requests.get(search_url_movie_details, headers=headers)
    movie_details = response.json()
    new_movie = Movie(
        title=movie_details["original_title"],
        img_url=f"{TMDB_IMG_URL}{movie_details['poster_path']}",
        year=movie_details["release_date"][0:4],
        description=movie_details["overview"]
    )
    db.session.add(new_movie)
    db.session.commit()
    new_movie_id = Movie.query.filter_by(title=movie_details["original_title"]).first().id
    return redirect(url_for('edit_movie', id=new_movie_id))


@app.route("/edit", methods=["GET", "POST"])
def edit_movie():
    rate_movie_form = RateMovieForm()
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    if rate_movie_form.validate_on_submit():
        movie_to_update.rating = rate_movie_form.rating.data
        movie_to_update.review = rate_movie_form.review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', movie=movie_to_update, form=rate_movie_form)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
