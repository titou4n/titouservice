import sqlite3
import os
from config import Config

conf = Config()

def init_database():
    db_path = conf.DATABASE_URL

    if os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # =========================
    # TABLE account
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS account (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        username STRING NOT NULL UNIQUE,
        password STRING NOT NULL,
        name STRING NOT NULL UNIQUE,
        pay DECIMAL DEFAULT 1000,
        nbpasswordchange INTEGER DEFAULT 0,
        nbnamechange INTEGER DEFAULT 0
    );
    """)

    # =========================
    # TABLE metadata
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metadata (
        id_metadata INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER NOT NULL,
        date_connected DATETIME NOT NULL,
        ipv4 INTEGER NOT NULL,
        FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
    );
    """)

    # =========================
    # TABLE bank_transfers
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bank_transfers (
        id_bank_transfer INTEGER PRIMARY KEY AUTOINCREMENT,
        id_sender INTEGER NOT NULL,
        id_receiver INTEGER NOT NULL,
        transfer_amount INTEGER NOT NULL,
        transfer_date DATETIME NOT NULL,
        FOREIGN KEY (id_sender) REFERENCES account(id) ON DELETE CASCADE,
        FOREIGN KEY (id_receiver) REFERENCES account(id) ON DELETE CASCADE
    );
    """)

    # =========================
    # TABLE posts
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id_post INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER NOT NULL,
        name STRING NOT NULL,
        title STRING NOT NULL,
        content STRING NOT NULL,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
    );
    """)

    # =========================
    # TABLE movie_search
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movie_search (
        id_movie_search INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER NOT NULL,
        movie_title STRING NOT NULL,
        date_movie_search DATETIME NOT NULL,
        FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("-> Base de données initialisée avec succès.")

def get_plan_database():
    print("Get plan database....")
    db_path = conf.DATABASE_URL
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    for row in cursor.fetchall():
        print(row[0])

    conn.close()

def reset_database():
    """
    Supprime l'ancienne base de données et la recrée avec toutes les tables.
    """
    db_path = conf.DATABASE_URL
    if os.path.exists(db_path):
        os.remove(db_path)
        print("-> Ancienne base de données supprimée.")
    
    init_database()

init_database()