import os
from pathlib import Path
from dotenv import load_dotenv
from utils.ipv4_address import ipv4_address

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

    ipv4_address = ipv4_address()
    print(f"IPV4 : {ipv4_address}")

    #       ||
    #       ||
    #       ||
    #      \  /
    #       \/

    #ENV_PROD = True if ipv4_address[:7] != "192.168" else False
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
    
    GMAIL_ADDRESS = "titouservice.mail@gmail.com"
    GMAIL_APP_PASSWORD = read_secret("gmail_app_password") if ENV_PROD else os.getenv("GMAIL_APP_PASSWORD")
    if not OMDB_API_KEY:
        raise RuntimeError("GMAIL_APP_PASSWORD manquante")
    
    #___________________________________________________#

    # ===== Base directory =====
    BASE_DIR = Path(__file__).parent.resolve()

    # ===== Flask =====
    if not ENV_PROD: # Valeur par défaut : production
        FLASK_ENV = "developpement"
    else:
        FLASK_ENV = "production"
    print(f"FLASK_ENV : {FLASK_ENV}")

    DEBUG = not ENV_PROD

    # ===== Flask-Session configuration =====
    SESSION_TYPE = "filesystem"                     # backend session
    SESSION_FILE_DIR = BASE_DIR / "flask_session"   # dossier temporaire pour stocker les sessions
    SESSION_PERMANENT = False                       # sessions non permanentes
    SESSION_USE_SIGNER = True                       # sécurise le cookie de session
    
    '''
    SESSION_COOKIE_NAME¶
    Le nom du cookie de session. Peut être modifié dans le cas où vous avez déjà un cookie avec le même nom.
    Valeur par défaut : session
    '''
    SESSION_COOKIE_NAME = "cookie_Titouservice"
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = None
    '''
    SESSION_COOKIE_HTTPONLY
    Pour des raisons de sécurité, les navigateurs ne permettent pas à JavaScript d’accéder aux cookies marqués « HTTP uniquement ».
    '''
    SESSION_COOKIE_HTTPONLY = True          # -> cookie inaccessible en JS
    '''
    SESSION_COOKIE_SECURE
    Les navigateurs n’enverront des cookies avec les demandes sur HTTPS que si le cookie est marqué « secure ».
    L’application doit être servie via HTTPS pour que cela ait un sens.
    Valeur par défaut : False
    '''
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE="Lax"

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

    # ===== Visitor =====
    USERNAME_VISITOR = "UsernameVisitor"
    PASSWORD_VISITOR = "PasswordVisitor"
    NAME_VISITOR = "Visitor"

    # ===== BANK =====
    BANK_DEFAULT_PAY = 1000000
    STOCK_MARKET_COEFFICIENT = 1