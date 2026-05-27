import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """
    Application configuration.

    Secrets are read from Docker secrets in production and from
    environment variables (via .env) in development.
    """

    # ─────────────────────────── Environment ────────────────────────────── #

    ENV_PROD: bool = True

    FLASK_ENV: str = "production" if ENV_PROD else "development"
    DEBUG: bool = not ENV_PROD

    if not ENV_PROD:
        load_dotenv()
    
    #_______________________KEY_________________________#

    @staticmethod
    def read_secret(name):
        try:
            with open(f"/run/secrets/{name}") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    SECRET_KEY = read_secret("secret_key") if ENV_PROD else os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is missing")
    
    USERNAME_SUPER_ADMIN: str = read_secret("username_super_admin") if ENV_PROD else os.getenv("USERNAME_SUPER_ADMIN")
    if not USERNAME_SUPER_ADMIN:
        raise RuntimeError("USERNAME_SUPER_ADMIN is missing")
    
    PASSWORD_SUPER_ADMIN: str = read_secret("password_super_admin") if ENV_PROD else os.getenv("PASSWORD_SUPER_ADMIN")
    if not PASSWORD_SUPER_ADMIN:
        raise RuntimeError("PASSWORD_SUPER_ADMIN is missing")

    ROLE_NAME_SUPER_ADMIN: str = "super_admin"
    NAME_SUPER_ADMIN: str = "SUPER ADMIN"
    
    TWELVEDATA_API_KEY = read_secret("twelvedata_api_key") if ENV_PROD else os.getenv("TWELVEDATA_API_KEY")
    if not TWELVEDATA_API_KEY:
        raise RuntimeError("TWELVEDATA_API_KEY is missing")

    OMDB_API_KEY = read_secret("omdb_api_key") if ENV_PROD else os.getenv("OMDB_API_KEY")
    if not OMDB_API_KEY:
        raise RuntimeError("OMDB_API_KEY is missing")
    
    EMAIL_ADDRESS = "titouservice.mail@gmail.com"
    EMAIL_APP_PASSWORD = read_secret("email_app_password") if ENV_PROD else os.getenv("EMAIL_APP_PASSWORD")
    if not EMAIL_APP_PASSWORD:
        raise RuntimeError("EMAIL_APP_PASSWORD is missing")

    # ──────────────────────────── Paths ─────────────────────────────────── #

    BASE_DIR: Path = Path(__file__).parent.resolve()
    DATA_DIR: Path = BASE_DIR / "Data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    DATABASE_FOLDER: Path = DATA_DIR / "db"
    DATABASE_FOLDER.mkdir(parents=True, exist_ok=True)
    DATABASE_URL: str             = str(DATABASE_FOLDER / "database.db")
    DATABASE_JOB_TRACKER_URL: str = str(DATABASE_FOLDER / "database_job_tracker.db")

    UPLOAD_FOLDER: Path = BASE_DIR / "static" / "uploads"
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    UPLOAD_PROFILE_PICTURE_FOLDER: Path = UPLOAD_FOLDER / "profile_pictures"
    UPLOAD_PROFILE_PICTURE_FOLDER.mkdir(parents=True, exist_ok=True)

    PATH_DEFAULT_PROFILE_PICTURE: Path = BASE_DIR / "static" / "img" / "profile-default.png"

    # ──────────────────────────── Uploads ───────────────────────────────── #

    MAX_CONTENT_LENGTH: int             = 16 * 1024 * 1024   # 16 MB
    ALLOWED_EXTENSIONS_PROFILE_PICTURE: set[str] = {"png", "jpg", "jpeg"}

    # ──────────────────────── Flask-Session ─────────────────────────────── #

    SESSION_TYPE: str            = "filesystem"
    SESSION_FILE_DIR: Path       = BASE_DIR / "flask_session"
    SESSION_PERMANENT: bool      = False
    SESSION_USE_SIGNER: bool     = True

    SESSION_COOKIE_NAME: str     = "cookie_Titouservice"
    SESSION_COOKIE_DOMAIN        = None
    SESSION_COOKIE_PATH          = None
    SESSION_COOKIE_HTTPONLY: bool = True          # Blocks JS access to the cookie
    SESSION_COOKIE_SECURE: bool  = ENV_PROD       # Requires HTTPS in production
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # Session lifetime
    SESSION_COOKIE_TIME_DAYS: int    = 0
    SESSION_COOKIE_TIME_HOURS: int   = 1
    SESSION_COOKIE_TIME_MINUTES: int = 0

    # 2FA code validity window
    TWOFA_TIMELAPS_MINUTES: int = 15

    # Password generation
    PASSWORD_GENERATION_LENGTH: int = 20

    # ─────────────────────── Redis ─────────────────────── #
    # Redis
    REDIS_URL: str = os.getenv(
        "RATELIMIT_STORAGE_URI",
        "redis://localhost:6379/0"
    )

    # ─────────────────────── Database reset flags ───────────────────────── #

    NEED_TO_RESET_DB_EXCEPT_ACCOUNT: bool        = False
    NEED_TO_RESET_ALL_DB: bool                   = True
    NEED_TO_RESET_ROLES_PERMISSIONS_TABLES: bool = True

    # Built-in accounts - SECURITY: disabled by default
    CREATE_SEEDED_ACCOUNTS: bool = False

    # ──────────────────────── Built-in accounts ─────────────────────────── #

    ROLE_NAME_SUPER_ADMIN: str = "super_admin"
    ROLE_NAME_ADMIN: str = "admin"

    USERNAME_VISITOR: str = "UsernameVisitor"
    PASSWORD_VISITOR: str = "PasswordVisitor"
    ROLE_NAME_VISITOR: str = "visitor"
    NAME_VISITOR: str = "Visitor"

    # Debug user (development only)
    USERNAME_DEBUG: str    = "11"
    PASSWORD_DEBUG: str    = "11"
    ROLE_NAME_DEBUG: str   = ROLE_NAME_SUPER_ADMIN
    NAME_DEBUG : str       = "DEBUG"

    # ─────────────────────────── Bank / Game ────────────────────────────── #

    BANK_DEFAULT_PAY: int         = 1_000_000
    STOCK_MARKET_COEFFICIENT: int = 1

    # =============================================== #
    # ============ Emergency information ============
    # =============================================== #
    """
    Configuration constants for the Emergency Information module.
    Override any value via environment variables or app.config before registering the blueprint.
    """
    
    TOKEN_LENGTH          = 48              # bytes → 64 hex chars (url-safe)
    TOKEN_URL_PREFIX      = '/emergency'    # public URL prefix
    ADMIN_PAGE_SIZE       = 25              # Pagination
    BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown']
    GENDER_OPTIONS = [
        ('male',            'Male'),
        ('female',          'Female'),
        ('other',           'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    RELATION_OPTIONS = [
        'Spouse', 'Partner', 'Parent', 'Child', 'Sibling',
        'Friend', 'Colleague', 'Neighbor', 'Other',
    ]

    MAX_TEXT_FIELD     = 5000
    MAX_SHORT_FIELD    = 150
    MAX_PHONE_FIELD    = 30

    PUBLIC_RATE_LIMIT  = 50 # Rate-limiting for public token access (requests / minute)