import os
from pathlib import Path
from dotenv import load_dotenv
import socket

def get_ipv4_host():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

def read_secret(name):
    try:
        with open(f"/run/secrets/{name}") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

class Config:

    #ipv4_address = get_ipv4_host()
    #ENV_PROD = not ipv4_address.startswith("192.168")
    ENV_PROD = False

    print(f"ENV_PROD : {ENV_PROD}")
    #print(f"IPV4 : {ipv4_address}")

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
    
    EMAIL_ADDRESS = "titouservice.mail@gmail.com"
    EMAIL_APP_PASSWORD = read_secret("email_app_password") if ENV_PROD else os.getenv("EMAIL_APP_PASSWORD")
    if not EMAIL_APP_PASSWORD:
        raise RuntimeError("EMAIL_APP_PASSWORD manquante")

    
    #___________________________________________________#

    # ===== Base directory =====
    BASE_DIR = Path(__file__).parent.resolve()

    # ===== Flask =====
    FLASK_ENV = "production" if ENV_PROD else "development"
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
    SESSION_COOKIE_SECURE = ENV_PROD
    SESSION_COOKIE_SAMESITE="Lax"

    SESSION_COOKIE_TIME_DAYS = 0
    SESSION_COOKIE_TIME_HOURS = 1
    SESSION_COOKIE_TIME_MINUTES = 0

    TWOFA_TIMELAPS_MINUTES = 15

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

    # ===== PERMISSIONS/ROLES =====
    LIST_ROLES = ["super_admin", "admin", "user", "visitor"]
    LIST_PERMISSIONS = [
            "access_admin_panel",
            "view_own_data"
        ]
    
    LIST_ADMIN_PERMS = ["access_admin_panel", "view_own_data"]
    LIST_USER_PERMS = ["view_own_data"]
    LIST_VISITOR_PERMS =[]

    

