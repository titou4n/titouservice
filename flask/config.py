import os
from pathlib import Path
from dotenv import load_dotenv

def read_secret(name):
    try:
        with open(f"/run/secrets/{name}") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    
###############################################
#_____DO_NOT_FORGET_TO_SWITCH_PROD_TO_DEV_____#
###############################################

class Config:

    #       ||
    #       ||
    #       ||
    #      \  /
    #       \/
    
    ENV_PROD = False

    #       /\
    #      /  \
    #       ||
    #       ||
    #       ||

    if not ENV_PROD:
        load_dotenv()

    #_______________________KEY_________________________#

    SECRET_KEY = read_secret("secret_key") if ENV_PROD else os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY manquante")
    
    TWELVEDATA_API_KEY = read_secret("twelvedata_api_key") if ENV_PROD else os.getenv("TWELVEDATA_API_KEY")
    if not TWELVEDATA_API_KEY:
        raise RuntimeError("TWELVEDATA_API_KEY manquante")

    OMDB_API_KEY = read_secret("omdb_api_key") if ENV_PROD else os.getenv("OMDB_API_KEY")
    if not OMDB_API_KEY:
        raise RuntimeError("OMDB_API_KEY manquante")
    
    #___________________________________________________#

    # ===== Base directory =====
    BASE_DIR = Path(__file__).parent.resolve()

    # ===== Flask =====
    DEBUG = not ENV_PROD

    # ===== Flask-Session configuration =====
    SESSION_TYPE = "filesystem"                     # backend session
    SESSION_FILE_DIR = BASE_DIR / "flask_session"   # dossier temporaire pour stocker les sessions
    SESSION_PERMANENT = False                       # sessions non permanentes
    SESSION_USE_SIGNER = True                       # sécurise le cookie de session
    SESSION_COOKIE_NAME = "cookie_Titouservice"     # nom du cookie
    SESSION_COOKIE_HTTPONLY = True                  # cookie inaccessible en JS

    # ===== Database =====
    DATA_DIR = BASE_DIR / "Data"
    DATA_DIR.mkdir(exist_ok=True)
    DATABASE_URL = os.path.join(DATA_DIR, "database.db")

    # ===== Uploads =====
    
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    UPLOAD_PROFILE_PICTURE_FOLDER = UPLOAD_FOLDER / "profile_pictures"
    UPLOAD_PROFILE_PICTURE_FOLDER.mkdir(exist_ok=True)
    ALLOWED_EXTENSIONS_PROFILE_PICTURE = {'png', 'jpg', 'jpeg'}

    # ===== DEFAULT =====
    PATH_DEFAULT_PROFILE_PICTURE = BASE_DIR / "static" / "img" / "profile-default.png"

    # ===== BANK =====
    BANK_DEFAULT_PAY = 1000000
    STOCK_MARKET_COEFFICIENT = 1