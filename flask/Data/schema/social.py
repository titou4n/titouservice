"""
Data/schema/social.py
---------------------
DDL for ``friends``, ``messages``, ``posts`` and ``movie_search`` tables.
Only CREATE TABLE / CREATE INDEX statements live here.
"""

SCHEMA_FRIENDS: str = """
CREATE TABLE IF NOT EXISTS friends (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL,
    followed_id INTEGER NOT NULL,
    date        TEXT    NOT NULL,
    UNIQUE (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES account(id) ON DELETE CASCADE,
    FOREIGN KEY (followed_id) REFERENCES account(id) ON DELETE CASCADE
);
"""

SCHEMA_MESSAGES: str = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id   INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message     TEXT    NOT NULL,
    datetime    TEXT    NOT NULL,
    FOREIGN KEY (sender_id)   REFERENCES account(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES account(id) ON DELETE CASCADE
);
"""

SCHEMA_POSTS: str = """
CREATE TABLE IF NOT EXISTS posts (
    id_post     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES account(id) ON DELETE CASCADE
);
"""

SCHEMA_MOVIE_SEARCH: str = """
CREATE TABLE IF NOT EXISTS movie_search (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    movie_title         TEXT    NOT NULL,
    date_movie_search   TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES account(id) ON DELETE CASCADE
);
"""

INDEX_FRIENDS_FOLLOWER: str = """
CREATE INDEX IF NOT EXISTS idx_friends_follower_id ON friends(follower_id);
"""

INDEX_FRIENDS_FOLLOWED: str = """
CREATE INDEX IF NOT EXISTS idx_friends_followed_id ON friends(followed_id);
"""

INDEX_MESSAGES_SENDER: str = """
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
"""

INDEX_MESSAGES_RECEIVER: str = """
CREATE INDEX IF NOT EXISTS idx_messages_receiver_id ON messages(receiver_id);
"""

INDEX_POSTS_USER_ID: str = """
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
"""

INDEX_MOVIE_SEARCH_USER_ID: str = """
CREATE INDEX IF NOT EXISTS idx_movie_search_user_id ON movie_search(user_id);
"""

ALL_STATEMENTS: list[str] = [
    SCHEMA_FRIENDS,
    SCHEMA_MESSAGES,
    SCHEMA_POSTS,
    SCHEMA_MOVIE_SEARCH,
    INDEX_FRIENDS_FOLLOWER,
    INDEX_FRIENDS_FOLLOWED,
    INDEX_MESSAGES_SENDER,
    INDEX_MESSAGES_RECEIVER,
    INDEX_POSTS_USER_ID,
    INDEX_MOVIE_SEARCH_USER_ID,
]
