import logging
from datetime import datetime, timedelta
from flask import request, session as flask_session
import secrets
import hashlib
import requests
import extensions as ext

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.db_session = ext.db_session_repository
        self.config = ext.config
        self._request_session = None

    def init_app(self, app_instance):
        self._request_session = requests.Session()

    def get_ip_session(self) -> str | None:
        try:
            session_id = flask_session.get("session_id")
            if not session_id:
                return None

            session_id_hash = self.hash_session_id(session_id=session_id)
            db_session = self.db_session.get_by_hash(session_id_hash=session_id_hash)

            if not db_session:
                return None

            if db_session.get("is_revoked", False):
                return None

            expires_at_str = db_session.get("expires_at")
            if not expires_at_str:
                return None

            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at < ext.utils.get_datetime_utc():
                self.revoke_session(session_id_hash)
                return None

            ip_hash_stored = db_session.get("ip_hash")
            if not ip_hash_stored:
                return None

            if ip_hash_stored != self.hash_ip(request.remote_addr or ""):
                self.revoke_session(session_id_hash)
                return None

            return request.remote_addr
        except Exception as e:
            logger.warning("Error in get_ip_session: %s", str(e))
            return None

    def get_ip_location(self, ip_address: str) -> str | None:
        if not ip_address:
            return None
        try:
            logger.info("Fetching IP location for: %s", ip_address)
            url = f"https://ipapi.co/{ip_address}/json/"
            response = self._request_session.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            if data.get("error") or "country_name" not in data:
                logger.warning("Invalid IP location response for %s", ip_address)
                return None

            return data.get("country_name")
        except Exception as e:
            logger.error("Error fetching IP location: %s", str(e))
            return None
    
    def get_location(self) -> str | None:
        ip = self.get_ip_session()
        if not ip:
            return None
        return self.get_ip_location(ip_address=ip)

    ############################################
    #_______________SESSION____________________#
    ############################################

    def generate_session_id(self) -> str:
        return secrets.token_urlsafe(32)
    
    def hash_session_id(self, session_id) -> str:
        return hmac.new(
            self.config.SECRET_KEY.encode(),
            session_id.encode(),
            hashlib.sha256
        ).hexdigest()

    def hash_ip(self, ip: str) -> str:
        return hmac.new(
            self.config.SECRET_KEY.encode(),
            ip.encode(),
            hashlib.sha256
        ).hexdigest()

    def hash_user_agent(self, user_agent: str) -> str:
        return hmac.new(
            self.config.SECRET_KEY.encode(),
            user_agent.encode(),
            hashlib.sha256
        ).hexdigest()

    def verif_session_is_active(self, session_id_hash: str) -> bool:
        try:
            db_session = self.db_session.get_by_hash(session_id_hash=session_id_hash)

            if not db_session:
                return False

            if db_session.get("is_revoked", False):
                return False

            expires_at_str = db_session.get("expires_at")
            if not expires_at_str:
                return False

            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at < ext.utils.get_datetime_utc():
                self.revoke_session(session_id_hash)
                return False

            ip_hash_stored = db_session.get("ip_hash")
            current_ip = request.remote_addr or ""
            if ip_hash_stored != self.hash_ip(current_ip):
                self.revoke_session(session_id_hash)
                return False

            ua_hash_stored = db_session.get("user_agent_hash")
            current_ua = request.headers.get("User-Agent", "")
            if ua_hash_stored != self.hash_user_agent(current_ua):
                self.revoke_session(session_id_hash)
                return False

            self.db_session.touch(
                session_id_hash=session_id_hash,
                last_used_at=ext.utils.get_datetime_utc()
            )
            return True
        except Exception as e:
            logger.error("Error verifying session: %s", str(e))
            return False

    def send_session(self, user_id:int) -> None:
        session_id = self.generate_session_id()
        session_id_hash = self.hash_session_id(session_id)

        ip_hash = self.hash_ip(request.remote_addr)
        ua_hash = self.hash_user_agent(request.headers.get("User-Agent", ""))
        now = ext.utils.get_datetime_utc()

        self.db_session.insert(
            session_id_hash=session_id_hash,
            user_id=user_id,
            ip_hash=ip_hash,
            user_agent_hash=ua_hash,
            created_at=now,
            expires_at=now + timedelta(days=self.config.SESSION_COOKIE_TIME_DAYS,
                                    hours=self.config.SESSION_COOKIE_TIME_HOURS,
                                    minutes=self.config.SESSION_COOKIE_TIME_MINUTES),
            is_revoked=0)

        flask_session["session_id"] = session_id

    def send_temp_2fa_session(self, user_id: int) -> None:
        """Crée une session temporaire pour la vérification 2FA uniquement"""
        temp_session_id = self.generate_session_id()
        flask_session["temp_2fa_session_id"] = temp_session_id
        flask_session["temp_user_id"] = user_id
        flask_session["temp_session_created_at"] = ext.utils.get_datetime_utc().isoformat()
        logger.info("Temporary 2FA session created for user %s", user_id)

    def verify_temp_2fa_session(self, user_id: int) -> bool:
        """Vérifie que la session temporaire 2FA est valide"""
        temp_user_id = flask_session.get("temp_user_id")
        if temp_user_id != user_id:
            logger.warning("2FA session user mismatch: expected %s, got %s", user_id, temp_user_id)
            return False

        created_at_str = flask_session.get("temp_session_created_at")
        if not created_at_str:
            return False

        try:
            created_at = datetime.fromisoformat(created_at_str)
            if ext.utils.get_datetime_utc() > created_at + timedelta(minutes=15):
                logger.warning("2FA session expired for user %s", user_id)
                return False
        except Exception as e:
            logger.error("Error verifying temp 2FA session: %s", str(e))
            return False

        return True

    def finalize_2fa_session(self, user_id: int) -> None:
        """Transforme la session temporaire 2FA en session réelle"""
        flask_session.pop("temp_2fa_session_id", None)
        flask_session.pop("temp_user_id", None)
        flask_session.pop("temp_session_created_at", None)
        self.send_session(user_id)
        logger.info("2FA session finalized for user %s", user_id)

    def revoke_session(self, session_id_hash:str) -> None:
        self.db_session.revoke(session_id_hash=session_id_hash)
        return None

    def get_session_info(self, session_id_hash:str):
        return self.db_session.get_by_hash(session_id_hash=session_id_hash)

    def get_current_session_id_hash(self) -> str | None:
        try:
            session_id = flask_session.get("session_id")
            if not session_id:
                return None

            session_id_hash = self.hash_session_id(session_id=session_id)
            if not self.verif_session_is_active(session_id_hash=session_id_hash):
                return None

            return session_id_hash
        except Exception as e:
            logger.error("Error getting current session hash: %s", str(e))
            return None
    
    def get_current_user_id(self) -> int | None:
        try:
            session_id = flask_session.get("session_id")
            if not session_id:
                return None

            session_id_hash = self.hash_session_id(session_id=session_id)
            if not self.verif_session_is_active(session_id_hash=session_id_hash):
                return None

            db_session = self.db_session.get_by_hash(session_id_hash=session_id_hash)
            if not db_session:
                return None

            user_id = db_session.get("user_id")
            return int(user_id) if user_id is not None else None
        except (ValueError, TypeError) as e:
            logger.error("Error retrieving current user ID: %s", str(e))
            return None
    
    def logout(self) -> None:
        try:
            session_id = flask_session.get("session_id")
            if not session_id:
                return

            session_id_hash = self.hash_session_id(session_id=session_id)
            db_session = self.db_session.get_by_hash(session_id_hash=session_id_hash)

            if db_session:
                self.revoke_session(session_id_hash)

            flask_session.clear()
            logger.info("User logged out successfully")
        except Exception as e:
            logger.error("Error during logout: %s", str(e))
            flask_session.clear()

    def logout_user_from_all_devices(self, user_id: int) -> None:
        try:
            session_id = flask_session.get("session_id")
            if not session_id:
                return

            session_id_hash = self.hash_session_id(session_id=session_id)
            db_session = self.db_session.get_by_hash(session_id_hash=session_id_hash)

            if db_session:
                self.revoke_session(session_id_hash)

            flask_session.clear()
            logger.info("User %s logged out from all devices", user_id)
        except Exception as e:
            logger.error("Error logging out user from all devices: %s", str(e))

    def logout_session(self, session_id_hash:str) -> None:
        self.db_session.revoke(session_id_hash=session_id_hash)

    def delete_session(self, session_id_hash:str) -> None:
        self.db_session.delete(session_id_hash=session_id_hash)