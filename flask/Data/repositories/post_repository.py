"""
Data/repositories/post_repository.py
--------------------------------------
CRUD operations for the ``posts`` table.
"""

import logging
import sqlite3
from typing import Optional

from Data.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class PostRepository:
    """Repository for community posts / chatroom entries."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        self._db = db_connection

    # ------------------------------------------------------------------ #
    # Create
    # ------------------------------------------------------------------ #

    def create(self, user_id: int, title: str, content: str) -> None:
        """Insert a new post."""
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO posts (user_id, title, content)
                VALUES (?, ?, ?);
                """,
                (user_id, title, content),
            )
            conn.commit()
        logger.debug("Post created by user_id=%d", user_id)

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #

    def get_all(self) -> list[sqlite3.Row]:
        """Return every post ordered by creation date (newest first)."""
        with self._db.connect() as conn:
            return conn.execute(
                "SELECT * FROM posts ORDER BY created_at DESC;",
            ).fetchall()

    def get_by_id(self, post_id: int) -> Optional[sqlite3.Row]:
        """Return a single post by *post_id*, or ``None``."""
        with self._db.connect() as conn:
            return conn.execute(
                "SELECT * FROM posts WHERE id_post = ?;",
                (post_id,),
            ).fetchone()

    def get_user_id_by_post_id(self, post_id: int) -> Optional[int]:
        """Return the *user_id* of the post author, or ``None``."""
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT user_id FROM posts WHERE id_post = ?;",
                (post_id,),
            ).fetchone()
        return row["user_id"] if row else None

    # ------------------------------------------------------------------ #
    # Update
    # ------------------------------------------------------------------ #

    def update(self, post_id: int, title: str, content: str) -> None:
        with self._db.connect() as conn:
            conn.execute(
                """
                UPDATE posts
                SET title = ?, content = ?
                WHERE id_post = ?;
                """,
                (title, content, post_id),
            )
            conn.commit()

    # ------------------------------------------------------------------ #
    # Delete
    # ------------------------------------------------------------------ #

    def delete(self, post_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "DELETE FROM posts WHERE id_post = ?;",
                (post_id,),
            )
            conn.commit()

    def delete_all_by_user_id(self, user_id: int) -> None:
        """Remove every post belonging to *user_id*."""
        with self._db.connect() as conn:
            conn.execute(
                "DELETE FROM posts WHERE user_id = ?;",
                (user_id,),
            )
            conn.commit()
        logger.info("All posts deleted for user_id=%d", user_id)
