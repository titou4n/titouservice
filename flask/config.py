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

    # ──────────────────────────── Helpers ───────────────────────────────── #

    @staticmethod
    def _read_secret(name: str) -> str | None:
        """Read a Docker secret from /run/secrets/<name>."""
        try:
            return Path(f"/run/secrets/{name}").read_text().strip()
        except FileNotFoundError:
            return None

    @classmethod
    def _get(cls, name: str) -> str:
        """Return a secret (prod) or env var (dev); raise if missing."""
        value = cls._read_secret(name) if cls.ENV_PROD else os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required secret / env var: {name!r}")
        return value
    
    # ─────────────────────────── Secret keys ────────────────────────────── #
    # Resolved after class definition (see bottom of file)
    SECRET_KEY: str
    TWELVEDATA_API_KEY: str
    OMDB_API_KEY: str
    EMAIL_ADDRESS: str        = "titouservice.mail@gmail.com"
    EMAIL_APP_PASSWORD: str

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

    # ─────────────────────── Database reset flags ───────────────────────── #

    NEED_TO_RESET_DB_EXCEPT_ACCOUNT: bool        = False
    NEED_TO_RESET_ALL_DB: bool                   = True
    NEED_TO_RESET_ROLES_PERMISSIONS_TABLES: bool = True

    # ──────────────────────── Built-in accounts ─────────────────────────── #

    USERNAME_SUPER_ADMIN: str = "super_admin"
    ROLE_NAME_SUPER_ADMIN: str = "super_admin"
    NAME_SUPER_ADMIN: str = "Super Admin"

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

    # ──────────────────────── Roles & permissions ───────────────────────── #

    LIST_DEFAULT_ROLES: list[str] = ["super_admin", "admin", "moderator", "user", "visitor"]

    # -- Permission groups --------------------------------------------------

    LIST_PERMISSIONS_USER: list[str] = [
        "view_own_profile",
        "edit_own_profile",
        "delete_own_account",
        "change_own_password",
        "export_own_data",
        "view_other_profile",
        "follow_profile",
    ]

    LIST_PERMISSIONS_USER_CONTENT: list[str] = [
        "view_content",
        "create_content",
        "edit_own_content",
        "delete_own_content",
        "view_messages",
        "create_messages",
        "edit_own_messages",
        "delete_own_messages",
    ]

    LIST_PERMISSIONS_MANAGE_CONTENT: list[str] = LIST_PERMISSIONS_USER_CONTENT + [
        "edit_all_content",
        "delete_all_content",
    ]

    LIST_PERMISSIONS_MANAGE_USERS: list[str] = [
        "view_users",
        "create_user",
        "edit_user",
        "delete_user",
        "ban_user",
        "assign_role",
    ]

    LIST_PERMISSIONS_MANAGE_ROLE: list[str] = [
        "view_roles",
        "create_role",
        "edit_role",
        "delete_role",
        "manage_permissions",
    ]

    LIST_PERMISSIONS_SYSTEM: list[str] = [
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

    LIST_ACCESS_SERVICES: list[str] = [
        "job_tracker_access",
    ]

    LIST_ALL_PERMISSIONS: list[str] = (
        LIST_PERMISSIONS_USER
        + LIST_PERMISSIONS_MANAGE_CONTENT
        + LIST_PERMISSIONS_MANAGE_USERS
        + LIST_PERMISSIONS_MANAGE_ROLE
        + LIST_PERMISSIONS_SYSTEM
        + LIST_ACCESS_SERVICES
    )

    # -- Per-role permission sets ------------------------------------------

    LIST_VISITOR_PERMS: list[str]   = ["view_content", "view_own_profile"]
    LIST_USER_PERMS: list[str]      = LIST_PERMISSIONS_USER + LIST_PERMISSIONS_USER_CONTENT + LIST_ACCESS_SERVICES
    LIST_MODERATOR_PERMS: list[str] = LIST_USER_PERMS + ["edit_all_content", "delete_all_content"]
    LIST_ADMIN_PERMS: list[str]     = LIST_ALL_PERMISSIONS

    # -- Lookup helpers ----------------------------------------------------

    DICT_PERMISSIONS_BY_TYPE: dict[str, list[str]] = {
        "user":           LIST_PERMISSIONS_USER,
        "manage_content": LIST_PERMISSIONS_MANAGE_CONTENT,
        "manage_users":   LIST_PERMISSIONS_MANAGE_USERS,
        "manage_role":    LIST_PERMISSIONS_MANAGE_ROLE,
        "system":         LIST_PERMISSIONS_SYSTEM,
    }

    DICT_ROLE_PERMISSION: dict[str, list[str]] = {
        "super_admin": LIST_ALL_PERMISSIONS,
        "admin":       LIST_ADMIN_PERMS,
        "moderator":   LIST_MODERATOR_PERMS,
        "user":        LIST_USER_PERMS,
        "visitor":     LIST_VISITOR_PERMS,
    }




# Resolve secrets now that the class is fully built and _get works correctly
Config.SECRET_KEY          = Config._get("SECRET_KEY")
Config.TWELVEDATA_API_KEY  = Config._get("TWELVEDATA_API_KEY")
Config.OMDB_API_KEY        = Config._get("OMDB_API_KEY")
Config.EMAIL_APP_PASSWORD  = Config._get("EMAIL_APP_PASSWORD")