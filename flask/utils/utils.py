from datetime import datetime, timedelta, timezone
import secrets


"""
utils/utils.py
--------------
Generic helper utilities shared across the application.
"""

import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Regex patterns
# ------------------------------------------------------------------ #

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


class Utils():
    def __init__(self):
        pass

    ############################################
    #_______________DATETIME___________________#
    ############################################

    def format_date(self, dt):
        if dt is None:
            return "—"

        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except ValueError:
                return dt

        return dt.astimezone().strftime("%d %b %Y")

    def format_datetime(self, dt):
        if dt is None:
            return "—"

        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except ValueError:
                return dt

        return dt.astimezone().strftime("%d %b %Y at %H:%M")
    
    def get_datetime_utc(self):
        return datetime.now(timezone.utc)

    def get_datetime_isoformat(self):
        return datetime.now(timezone.utc).isoformat()

    def get_datetime_plus_timedelta(self, timedelta_days= 0, timedelta_hours=0, timedelta_minutes=0):
        return self.get_datetime + timedelta(days=timedelta_days,
                                                       hours=timedelta_hours,
                                                       minutes=timedelta_minutes)
    
    def datetime_is_expired_minutes(self, datetime_created, timedelta_minutes):
        return datetime.now(timezone.utc) > datetime_created + timedelta(minutes=timedelta_minutes)
    
    ############################################
    #_______________PASSWORD___________________#
    ############################################

    def generate_password(self, size:int) -> str:
        return secrets.token_urlsafe(size)
    


    """Collection of application-level utility methods."""

    # ------------------------------------------------------------------ #
    # Date / time
    # ------------------------------------------------------------------ #

    @staticmethod
    def now_utc_str() -> str:
        """Return the current UTC datetime as an ISO-8601 string."""
        return datetime.now(tz=timezone.utc).isoformat()

    @staticmethod
    def now_utc() -> datetime:
        """Return the current UTC-aware :class:`datetime`."""
        return datetime.now(tz=timezone.utc)

    # ------------------------------------------------------------------ #
    # Validation helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Return ``True`` if *email* looks syntactically valid."""
        return bool(_EMAIL_RE.match(email))

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """
        Return ``True`` if *username* is 3–32 characters and contains
        only letters, digits, underscores, hyphens and dots.
        """
        return bool(_USERNAME_RE.match(username))

    @staticmethod
    def sanitise_string(value: str) -> str:
        """Strip leading/trailing whitespace from *value*."""
        return value.strip()
    
