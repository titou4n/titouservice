import os
from pathlib import Path

def read_secret(name):
    try:
        with open(f"/run/secrets/{name}") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

class Config:
    # ===== Sécurité =====
    SECRET_KEY = (
        read_secret("secret_key")
        or os.getenv("SECRET_KEY")
        or "dev-secret-key"
    )
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY manquante")

    # ===== Base directory =====
    BASE_DIR = Path(__file__).parent.resolve()

    # ===== Flask =====
    FLASK_ENV = "development"
    DEBUG = FLASK_ENV == "development"

    # ===== Flask-Session configuration =====
    SESSION_TYPE = "filesystem"             # backend session
    SESSION_FILE_DIR = BASE_DIR / "flask_session"  # dossier temporaire pour stocker les sessions
    SESSION_PERMANENT = False               # sessions non permanentes
    SESSION_USE_SIGNER = True               # sécurise le cookie de session
    SESSION_COOKIE_NAME = "my_session"      # nom du cookie
    SESSION_COOKIE_HTTPONLY = True          # cookie inaccessible en JS

    # ===== Database =====
    DATA_DIR = BASE_DIR / "Data"
    DATA_DIR.mkdir(exist_ok=True)
    DATABASE_URL = os.path.join(DATA_DIR, "database.db")

    # ===== Uploads =====
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # ===== External APIs =====
    OMDB_API_KEY = (
        read_secret("omdb_api_key")
        or os.getenv("OMDB_API_KEY")
        or "dev-omdb_api_key"
    )
    if not SECRET_KEY:
        raise RuntimeError("OMDB_API_KEY manquante")
