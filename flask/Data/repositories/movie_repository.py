"""
Data/repositories/movie_repository.py
---------------------------------------
CRUD operations for the ``movie_search`` table.
"""

import logging
import sqlite3

from Data.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class MovieRepository:
    """Repository for movie-search history per user."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        self._db = db_connection

    # ------------------------------------------------------------------ #
    # Create
    # ------------------------------------------------------------------ #

    def insert_search(
        self,
        user_id: int,
        movie_title: str,
        date_movie_search: str,
    ) -> None:
        """Record that *user_id* searched for *movie_title*."""
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO movie_search (user_id, movie_title, date_movie_search)
                VALUES (?, ?, ?);
                """,
                (user_id, movie_title, date_movie_search),
            )
            conn.commit()
        logger.debug(
            "Movie search recorded: user_id=%d, title=%s", user_id, movie_title
        )

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #

    def get_searches_by_user_id(self, user_id: int) -> list[sqlite3.Row]:
        """Return all movie searches performed by *user_id*."""
        with self._db.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM movie_search
                WHERE user_id = ?
                ORDER BY date_movie_search DESC;
                """,
                (user_id,),
            ).fetchall()

    def has_already_searched(self, user_id: int, movie_title: str) -> bool:
        """
        Return ``True`` if *user_id* has previously searched *movie_title*.
        """
        with self._db.connect() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM movie_search
                WHERE user_id = ? AND movie_title = ?
                LIMIT 1;
                """,
                (user_id, movie_title),
            ).fetchone()
        return row is not None
