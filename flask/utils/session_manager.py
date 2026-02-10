from datetime import datetime, timedelta
from flask_session import Session
from flask import sessions, request, session as flask_session
from Data.database_handler import DatabaseHandler
from utils.utils import Utils
from config import Config
import secrets
import hashlib
import requests

class SessionManager():
    def __init__(self, app_instance):
        Session(app=app_instance)
        self.database_handler = DatabaseHandler()
        self.utils = Utils()
        self.config = Config()

    ############################################
    #__________________IP______________________#
    ############################################

    def get_ip_session(self)  -> (str|None):
        session_id = flask_session.get("session_id")

        if not session_id:
            return None
        
        session_id_hash = self.hash_session_id(session_id=session_id)
        db_session = self.database_handler.get_session(session_id_hash=session_id_hash)
            
        if not db_session:
            return None
        
        if db_session["is_revoked"]:
            return None
        
        
        expires_at = datetime.fromisoformat(db_session["expires_at"])
        if expires_at < self.utils.get_datetime_utc():
            self.revoke_session(session_id_hash)
            return None
    
        if db_session["ip_hash"] != self.hash_ip(request.remote_addr):
            self.revoke_session(session_id_hash)
            return None

        return request.remote_addr

    def get_ip_location(self, ip_adress:str) -> (str|None):
        print(ip_adress)
        url = f"https://ipapi.co/{ip_adress}/json/"
        response = requests.get(url)
        data = response.json()
        if "error" in data and data["error"] or "country_name" not in data:
            return None
        return data["country_name"]
    
    def get_location(self) -> (str|None):
        return self.get_ip_location(ip_adress=self.get_ip_session())

    ############################################
    #_______________SESSION____________________#
    ############################################

    def generate_session_id(self) -> str:
        return secrets.token_urlsafe(32)
    
    def hash_session_id(self, session_id) -> str:
        return hashlib.sha256(session_id.encode()).hexdigest()
    
    def hash_ip(self, ip: str) -> str:
        return hashlib.sha256(ip.encode()).hexdigest()
    
    def hash_user_agent(self, user_agent: str) -> str:
        return hashlib.sha256(user_agent.encode()).hexdigest()

    def verif_session_is_active(self, session_id_hash:str) -> bool:
        db_session = self.database_handler.get_session(session_id_hash=session_id_hash)
            
        if not db_session:
            return None
        
        if db_session["is_revoked"]:
            return False
        
        expires_at = datetime.fromisoformat(db_session["expires_at"])
        if expires_at < self.utils.get_datetime_utc():
            self.revoke_session(session_id_hash)
            return False
    
        if db_session["ip_hash"] != self.hash_ip(request.remote_addr):
            self.revoke_session(session_id_hash)
            return False

        if db_session["user_agent_hash"] != self.hash_user_agent(request.headers.get("User-Agent", "")):
            self.revoke_session(session_id_hash)
            return False
        
        self.database_handler.update_session(session_id_hash=session_id_hash,
                                             last_used_at=self.utils.get_datetime_utc())
        return True

    def send_session(self, user_id:int) -> None:
        session_id = self.generate_session_id()
        session_id_hash = self.hash_session_id(session_id)

        ip_hash = self.hash_ip(request.remote_addr)
        ua_hash = self.hash_user_agent(request.headers.get("User-Agent", ""))
        now = self.utils.get_datetime_utc()

        self.database_handler.insert_session(session_id_hash=session_id_hash,
                                             user_id=user_id,
                                             ip_hash=ip_hash,
                                             user_agent_hash=ua_hash,
                                             created_at=now,
                                             expires_at=now + timedelta(days=self.config.SESSION_COOKIE_TIME_DAYS,
                                                                        hours=self.config.SESSION_COOKIE_TIME_HOURS,
                                                                        minutes=self.config.SESSION_COOKIE_TIME_MINUTES),
                                             is_revoked=0)

        flask_session["session_id"] = session_id

    def revoke_session(self, session_id_hash:str) -> None:
        self.database_handler.revoke_session(session_id_hash=session_id_hash)
        return None

    def get_session_info(self, session_id_hash:str):
        return self.database_handler.get_session(session_id_hash=session_id_hash)

    def get_current_session_id_hash(self) -> (str|None):
        session_id = flask_session.get("session_id")

        if not session_id:
            return None
        
        session_id_hash = self.hash_session_id(session_id=session_id)
        if not self.verif_session_is_active(session_id_hash=session_id_hash):
            return None

        return session_id_hash
    
    def get_current_user_id(self) -> (int|None):
        session_id = flask_session.get("session_id")

        if not session_id:
            return None
        
        session_id_hash = self.hash_session_id(session_id=session_id)
        if not self.verif_session_is_active(session_id_hash=session_id_hash):
            return None

        db_session = self.database_handler.get_session(session_id_hash=session_id_hash)
        return db_session["user_id"]
    
    def logout(self) -> None:
        session_id = flask_session.get("session_id")
        if not session_id:
            return None
        
        session_id_hash = self.hash_session_id(session_id=session_id)
        db_session = self.database_handler.get_session(session_id_hash=session_id_hash)
            
        if not db_session:
            return None

        self.revoke_session(session_id_hash)
        flask_session.clear()

    def logout_user_from_all_devices(self, user_id:int) -> None:
        session_id = flask_session.get("session_id")
        if not session_id:
            return None
        
        session_id_hash = self.hash_session_id(session_id=session_id)
        db_session = self.database_handler.get_session(session_id_hash=session_id_hash)
            
        if not db_session:
            return None

        self.revoke_session(session_id_hash)
        flask_session.clear()

    def logout_session(self, session_id_hash:str) -> None:
        self.database_handler.revoke_session(session_id_hash=session_id_hash)

    def delete_session(self, session_id_hash:str) -> None:
        self.database_handler.delete_session(session_id_hash=session_id_hash)

    ############################################
    #_______________METADATA___________________#
    ############################################

    def insert_metadata(self) -> None:
        self.database_handler.insert_metadata(self.get_current_user_id(),
                                              self.utils.get_datetime_isoformat(),
                                              self.get_ip_session())