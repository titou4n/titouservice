# blueprints/api/routes.py
# Préfixe : /api  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required

from blueprints.api import bp
from blueprints.api.services import search_movie
import extensions as ext


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@login_required
def api_home():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('api/api_home.html', id=user_id)


# ── Recherche de films (OMDB) ─────────────────────────────────────────────────

@bp.route('/search_movie', methods=['GET', 'POST'])
@bp.route('/search_movie/', methods=['GET', 'POST'])
@login_required
def api_search_movie():
    user_id = ext.session_manager.get_current_user_id()

    if request.method == 'GET':
        all_movie_search = ext.database_handler.get_movie_search(user_id)
        return render_template('api/api_search_movie.html',
                               id=user_id,
                               all_movie_search=all_movie_search)

    movie = str(request.form.get('movie', '')).strip()
    if not movie:
        flash('Movie title is required.')
        return redirect(url_for('api.api_search_movie'))

    return redirect(url_for('api.api_infos_movie', movie_title=movie))


@bp.route('/infos_movie/<string:movie_title>', methods=['GET'])
@bp.route('/infos_movie/<string:movie_title>/', methods=['GET'])
@login_required
def api_infos_movie(movie_title: str):
    user_id = ext.session_manager.get_current_user_id()

    if not movie_title:
        flash('Movie title is required.')
        return redirect(url_for('api.api_search_movie'))

    data, error = search_movie(movie_title)
    if error:
        flash(f'"{error}"')
        return redirect(url_for('api.api_search_movie'))

    # Sauvegarde de l'historique de recherche (dédupliqué)
    clean_title = data["Title"]
    if not ext.database_handler.movie_already_search(user_id, movie_title=clean_title):
        ext.database_handler.insert_movie_search(user_id, clean_title, ext.utils.get_datetime_isoformat())

    return render_template(
        'api/api_infosmovie.html',
        id=user_id,
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