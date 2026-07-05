# extensions.py

import ipaddress
import logging
import os
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

logger = logging.getLogger(__name__)

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

# Official Cloudflare IP ranges (https://www.cloudflare.com/ips/).
# CF-Connecting-IP is only trustworthy if the request actually reached us
# through Cloudflare — i.e. the immediate TCP peer address is one of these.
_CLOUDFLARE_CIDRS = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
    "2400:cb00::/32", "2606:4700::/32", "2803:f800::/32", "2405:b500::/32",
    "2405:8100::/32", "2a06:98c0::/29", "2c0f:f248::/32",
]
_CLOUDFLARE_NETWORKS = [ipaddress.ip_network(cidr) for cidr in _CLOUDFLARE_CIDRS]


def _parse_trusted_networks(raw: str) -> list:
    networks = []
    for cidr in raw.split(","):
        cidr = cidr.strip()
        if not cidr:
            continue
        try:
            networks.append(ipaddress.ip_network(cidr))
        except ValueError:
            logger.warning("Ignoring invalid entry in TRUSTED_PROXY_NETWORKS.")
    return networks


def _ip_in_networks(ip_value: str, networks: list) -> bool:
    """Real CIDR membership test — never a string/prefix comparison."""
    if not ip_value:
        return False
    try:
        ip = ipaddress.ip_address(ip_value)
    except ValueError:
        return False
    return any(ip in net for net in networks)


def get_client_identifier():
    """
    Real client IP for rate-limiting, trusting a proxy header only when the
    immediate TCP peer (request.remote_addr) is itself a known-trustworthy
    address — never just because the header is present (headers are fully
    attacker-controlled otherwise).

    Priority:
      1. CF-Connecting-IP, but only if remote_addr is a real Cloudflare IP.
      2. X-Forwarded-For, but only if remote_addr is in TRUSTED_PROXY_NETWORKS
         (e.g. Nginx Proxy Manager reaching this app directly, without Cloudflare).
      3. Fallback: the direct connection IP (no proxy trusted).
    """
    remote_addr = request.remote_addr

    if _ip_in_networks(remote_addr, _CLOUDFLARE_NETWORKS):
        cf_ip = request.headers.get('CF-Connecting-IP')
        if cf_ip:
            return cf_ip.strip()

    if _ip_in_networks(remote_addr, _TRUSTED_INTERNAL_NETWORKS):
        x_forwarded = request.headers.get('X-Forwarded-For')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()

    return get_remote_address()

# Config
config = Config()
permissions = Permissions()

# Parsed once at import time (not per-request) from config.TRUSTED_PROXY_NETWORKS
_TRUSTED_INTERNAL_NETWORKS = _parse_trusted_networks(config.TRUSTED_PROXY_NETWORKS)

# Flask Extensions
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=config.REDIS_URL,
    strategy="fixed-window",
    headers_enabled=True,
    default_limits=[]
)

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
