# blueprints/movie_information/routes.py
# Préfixe : /movie_information  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user

from blueprints.movie_information import bp
from blueprints.movie_information.services import search_movie_by_title
import extensions as ext


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@login_required
def movie_information_home():
    return render_template('movie_information/movie_information_home.html', id=current_user.id)


# ── Recherche de films (OMDB) ─────────────────────────────────────────────────

@bp.route('/search_movie', methods=['GET', 'POST'])
@bp.route('/search_movie/', methods=['GET', 'POST'])
@login_required
def search_movie():

    if request.method == 'GET':
        all_movie_search = ext.db_movie_repository.get_searches_by_user_id(current_user.id)
        return render_template('movie_information/search_movie.html',
                               id=current_user.id,
                               all_movie_search=all_movie_search)

    movie = str(request.form.get('movie', '')).strip()
    if not movie:
        flash('Movie title is required.')
        return redirect(url_for('movie_information.search_movie'))

    return redirect(url_for('movie_information.infos_movie', movie_title=movie))


@bp.route('/infos_movie/<string:movie_title>', methods=['GET'])
@bp.route('/infos_movie/<string:movie_title>/', methods=['GET'])
@login_required
def infos_movie(movie_title: str):

    if not movie_title:
        flash('Movie title is required.')
        return redirect(url_for('movie_information.search_movie'))

    data, error = search_movie_by_title(movie_title)
    if error:
        flash(f'"{error}"')
        return redirect(url_for('movie_information.search_movie'))

    # Sauvegarde de l'historique de recherche (dédupliqué)
    clean_title = data["Title"]
    if not ext.db_movie_repository.has_already_searched(current_user.id, movie_title=clean_title):
        ext.db_movie_repository.insert_search(current_user.id, clean_title, ext.utils.get_datetime_isoformat())

    return render_template(
        'movie_information/infosmovie.html',
        id=current_user.id,
        movie_title    = clean_title,
        movie_year     = data["Year"],
        movie_released = data["Released"],
        movie_runtime  = data["Runtime"],
        movie_genre    = data["Genre"],
        movie_director = data["Director"],
        movie_plot     = data["Plot"],
        movie_poster   = data["Poster"],
        movie_rating   = data["imdbRating"],
    )
