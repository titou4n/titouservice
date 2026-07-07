"""
Data/repositories/social_repository.py
----------------------------------------
CRUD operations for the ``friends`` and ``messages`` tables.
"""

import logging
import sqlite3

from Data.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SocialRepository:
    """Repository for the social-network follow graph and private messages."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        self._db = db_connection

    # ------------------------------------------------------------------ #
    # Follow graph
    # ------------------------------------------------------------------ #

    def follow(
        self,
        follower_id: int,
        followed_id: int,
        date: str,
    ) -> None:
        """Create a follower → followed link."""
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO friends (follower_id, followed_id, date)
                VALUES (?, ?, ?);
                """,
                (follower_id, followed_id, date),
            )
            conn.commit()
        logger.debug("Follow link: %d → %d", follower_id, followed_id)

    def unfollow(self, follower_id: int, followed_id: int) -> None:
        """Remove the follower → followed link."""
        with self._db.connect() as conn:
            conn.execute(
                """
                DELETE FROM friends
                WHERE follower_id = ? AND followed_id = ?;
                """,
                (follower_id, followed_id),
            )
            conn.commit()

    def is_following(self, follower_id: int, followed_id: int) -> bool:
        """Return ``True`` if *follower_id* follows *followed_id*."""
        with self._db.connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM friends
                WHERE follower_id = ? AND followed_id = ?;
                """,
                (follower_id, followed_id),
            ).fetchone()
        return row is not None

    def get_followers(self, user_id: int) -> list[sqlite3.Row]:
        """Return all rows where *user_id* is being followed."""
        with self._db.connect() as conn:
            return conn.execute(
                "SELECT follower_id FROM friends WHERE followed_id = ?;",
                (user_id,),
            ).fetchall()

    def get_followings(self, user_id: int) -> list[sqlite3.Row]:
        """Return all rows where *user_id* is the follower."""
        with self._db.connect() as conn:
            return conn.execute(
                "SELECT followed_id FROM friends WHERE follower_id = ?;",
                (user_id,),
            ).fetchall()

    # ------------------------------------------------------------------ #
    # Private messages
    # ------------------------------------------------------------------ #

    def send_message(
        self,
        sender_id: int,
        receiver_id: int,
        message: str,
        sent_at: str,
    ) -> None:
        """Persist a private message between two users."""
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (sender_id, receiver_id, message, datetime)
                VALUES (?, ?, ?, ?);
                """,
                (sender_id, receiver_id, message, sent_at),
            )
            conn.commit()

    def get_conversation(
        self,
        user_id_a: int,
        user_id_b: int,
    ) -> list[sqlite3.Row]:
        """Return all messages exchanged between two users (both directions)."""
        with self._db.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM messages
                WHERE (sender_id = ? AND receiver_id = ?)
                   OR (sender_id = ? AND receiver_id = ?)
                ORDER BY datetime ASC;
                """,
                (user_id_a, user_id_b, user_id_b, user_id_a),
            ).fetchall()
