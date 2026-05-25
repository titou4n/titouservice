# extensions.py

from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from Data.database_manager import DatabaseManager
from Data.database_job_tracker import DatabaseJobTracker
from Data.connection import DatabaseConnection

from Data.seeders.roles_permissions import RolesPermissionsSeeder
from Data.seeders.accounts_seeder   import AccountsSeeder

from Data.repositories.account_repository           import AccountRepository
from Data.repositories.bank_repository              import BankRepository
from Data.repositories.movie_repository             import MovieRepository
from Data.repositories.post_repository              import PostRepository
from Data.repositories.role_repository              import RoleRepository
from Data.repositories.session_repository           import SessionRepository
from Data.repositories.social_repository            import SocialRepository
from Data.repositories.twofa_repository             import TwoFARepository
from Data.repositories.emergency_information_repository import EmergencyInformationRepository

from config import Config
from utils.utils import Utils
from utils.session_manager import SessionManager
from utils.permissions_manager import PermissionsManager
from utils.email_manager import EmailManager
from utils.hash_manager import HashManager
from utils.bank_manager import BankManager
from utils.twofa_manager import TwofaManager
from utils.twelvedata_manager import TwelveDataManager
from utils.stock_market_manager import StockMarketManager
from utils.view_data import ViewDataWithMatplolib
from utils.decorators import *

from permissions import Permissions

# Flask Extensions
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Config
config = Config()
permissions = Permissions()

# Shared connection factory ─ one per process
db_connection = DatabaseConnection(db_path=config.DATABASE_URL)

# Initialise the schema + seeders
_db_manager = DatabaseManager(db_connection)

# ------------------------------------------------------------------ #
# Repository singletons
# ------------------------------------------------------------------ #

db_account_repository: AccountRepository = AccountRepository(db_connection)
db_role_repository: RoleRepository = RoleRepository(db_connection)
db_session_repository: SessionRepository = SessionRepository(db_connection)
db_twofa_repository: TwoFARepository = TwoFARepository(db_connection)
db_bank_repository: BankRepository = BankRepository(db_connection)
db_social_repository: SocialRepository = SocialRepository(db_connection)
db_post_repository: PostRepository = PostRepository(db_connection)
db_movie_repository: MovieRepository = MovieRepository(db_connection)
db_emergency_information_repository: EmergencyInformationRepository = EmergencyInformationRepository(db_connection)

database_job_tracker = DatabaseJobTracker()

# ------------------------------------------------------------------ #
# Service singletons
# ------------------------------------------------------------------ #

from blueprints.emergency_information.service import EmergencyInformationService

emergency_information_service: EmergencyInformationService = EmergencyInformationService(db_emergency_information_repository)

# Manager
session_manager = SessionManager()
permission_manager = PermissionsManager()
email_manager = EmailManager()
hash_manager = HashManager()
bank_manager = BankManager()
twofa_manager = TwofaManager()
stock_market_manager = StockMarketManager()
twelve_data_manager = TwelveDataManager()

# Utils/Tools
utils = Utils()
view_data = ViewDataWithMatplolib()

# Initialise seeders
_roles_permissions_seeders = RolesPermissionsSeeder()
_accounts_seeder = AccountsSeeder(
    config=config,
    account_repo=db_account_repository,
    role_repo=db_role_repository,
    hash_manager=hash_manager,
)
