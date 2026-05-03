# extensions.py
# Toutes les instances partagées, importables par les blueprints sans import circulaire.

from flask_login import LoginManager
from flask_wtf import CSRFProtect

from Data.database_handler import DatabaseHandler
from Data.database_job_tracker import DatabaseJobTracker
from Data.init_db import DatabaseManager
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

# Flask Extensions
login_manager = LoginManager()
csrf = CSRFProtect()

# Config
config = Config()

# Data
database_handler = DatabaseHandler()
database_manager = DatabaseManager()
database_job_tracker = DatabaseJobTracker()

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
view_data = ViewDataWithMatplolib(utils=utils, database_handler=database_handler)