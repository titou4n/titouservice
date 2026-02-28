import os
from pathlib import Path
from dotenv import load_dotenv

class Config:

    ENV_PROD = False

    print(f"ENV_PROD : {ENV_PROD}")

    if not ENV_PROD:
        load_dotenv()

    #_______________________KEY_________________________#

    def read_secret(name):
        try:
            with open(f"/run/secrets/{name}") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

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

    # ===== SUPER_ADMIN =====
    USERNAME_SUPER_ADMIN = "super_admin"
    ROLE_NAME_SUPER_ADMIN = "super_admin"
    NAME_SUPER_ADMIN = "Super Admin"

    ROLE_NAME_ADMIN = "admin"

    # ===== Visitor =====
    USERNAME_VISITOR = "UsernameVisitor"
    PASSWORD_VISITOR = "PasswordVisitor"
    ROLE_NAME_VISITOR = "visitor"
    NAME_VISITOR = "Visitor"

    # ===== DEBUG USER =====
    USERNAME_DEBUG = str(11)
    PASSWORD_DEBUG = str(11)
    ROLE_NAME_DEBUG = ROLE_NAME_SUPER_ADMIN

    # ===== BANK =====
    BANK_DEFAULT_PAY = 1000000
    STOCK_MARKET_COEFFICIENT = 1

    # ===== PERMISSIONS/ROLES =====
    LIST_DEFAULT_ROLES = ["super_admin", "admin", "moderator","user", "visitor"]

    LIST_PERMISSIONS_USER = [
        # Permission User
        "view_own_profile",
        "edit_own_profile",
        "delete_own_account",
        "change_own_password",
        "export_own_data",

        "view_other_profile",
        "follow_profile",
        ]
    
    LIST_PERMISSIONS_USER_CONTENT = [
        # Permission content
        "view_content",
        "create_content",
        "edit_own_content",
        "delete_own_content",

        "view_messages",
        "create_messages",
        "edit_own_messages",
        "delete_own_messages",
        ]
    
    LIST_PERMISSIONS_MANAGE_CONTENT = (LIST_PERMISSIONS_USER_CONTENT + ["edit_all_content", "delete_all_content",])

    LIST_PERMISSIONS_MANAGE_USERS = [
        # Permission - manage users
        "view_users",
        "create_user",
        "edit_user",
        "delete_user",
        "ban_user",
        "assign_role",
        ]

    LIST_PERMISSIONS_MANAGE_ROLE = [
        # Permission - manage role
        "view_roles",
        "create_role",
        "edit_role",
        "delete_role",
        "manage_permissions",
        ]
    
    LIST_PERMISSIONS_SYSTEM = [
        # Permission - SYSTEM
        "access_admin_panel",
        "view_logs",
        "manage_settings",
        "backup_database",
        "restore_database",

        "export_data",
        "import_data",
        "access_statistics",
        "moderate_comments",
        "view_sensitive_data",
        ]
    
    LIST_ALL_PERMISSIONS = (  LIST_PERMISSIONS_USER
                            + LIST_PERMISSIONS_MANAGE_CONTENT
                            + LIST_PERMISSIONS_MANAGE_USERS
                            + LIST_PERMISSIONS_MANAGE_ROLE
                            + LIST_PERMISSIONS_SYSTEM)
    
    LIST_VISITOR_PERMS =["view_content",
                         "view_own_profile",]
    
    LIST_USER_PERMS = LIST_PERMISSIONS_USER + LIST_PERMISSIONS_USER_CONTENT
    
    LIST_MODERATOR_PERMS = LIST_USER_PERMS + ["edit_all_content", "delete_all_content"]

    LIST_ADMIN_PERMS = LIST_ALL_PERMISSIONS

    DICT_PERMISSIONS_BY_TYPE = {
        "LIST_PERMISSIONS_USER":LIST_PERMISSIONS_USER,
        "LIST_PERMISSIONS_MANAGE_CONTENT":LIST_PERMISSIONS_MANAGE_CONTENT,
        "LIST_PERMISSIONS_MANAGE_USERS":LIST_PERMISSIONS_MANAGE_USERS,
        "LIST_PERMISSIONS_MANAGE_ROLE":LIST_PERMISSIONS_MANAGE_ROLE,
        "LIST_PERMISSIONS_SYSTEM":LIST_PERMISSIONS_SYSTEM,
    }

    DICT_ROLE_PERMISSION = {
        "super_admin":LIST_ALL_PERMISSIONS,
        "admin":LIST_ADMIN_PERMS,
        "moderator":LIST_MODERATOR_PERMS,
        "user":LIST_USER_PERMS,
        "visitor":LIST_VISITOR_PERMS
        }