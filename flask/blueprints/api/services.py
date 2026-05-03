# blueprints/api/services.py
# Logique d'appel à l'API OMDB. Isolée de la route pour être testable sans Flask.

import requests
from flask import current_app


def search_movie(title: str) -> tuple[dict | None, str | None]:
    """
    Interroge OMDB pour un titre de film.
    Retourne (movie_data: dict, error: str|None).
    movie_data est None si le film n'existe pas ou si l'API échoue.
    """
    api_key = current_app.config.get('OMDB_API_KEY', '')
    url     = f"http://www.omdbapi.com/?apikey={api_key}&t={title}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return None, f"Network error: {e}"

    if data.get("Response") == "False":
        return None, data.get("Error", "Movie not found.")

    return data, None
