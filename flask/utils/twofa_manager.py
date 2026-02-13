from Data.database_handler import DatabaseHandler
from utils.utils import Utils
from utils.hash_manager import HashManager
from utils.email_manager import EmailManager
from config import Config
import datetime

import random

class TwofaManager():
    def __init__(self):
        self.database_handler = DatabaseHandler()
        self.email_manager = EmailManager()
        self.hash_manager = HashManager()
        self.config = Config()
        self.utils = Utils()

    def generate_code(self) -> int:
        return random.randint(100000,999999)

    def send_code(self, user_id:int) -> None:
        random_code = self.generate_code()
        self.email_manager.send_two_factor_authentication_code_with_html(user_id, random_code)
        self.database_handler.insert_two_factor_codes(user_id=user_id,
                                                      code_hash=self.hash_manager.generate_password_hash(str(random_code)),
                                                      created_at=self.utils.get_datetime_isoformat())

    def verif_code(self, code:int, user_id:int) -> bool:

        code_hash = self.database_handler.get_code_hash_from_user_id(user_id=user_id)
        if code_hash is None:
            self.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
            return False
        
        if code_hash["used"]:
            self.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
            return False
        
        if code_hash["attempts"] >= 3:
            self.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
            return False
        
        created_at = datetime.fromisoformat(code_hash["created_at"])
        if self.utils.datetime_is_expired_minutes(created_at, self.config.TWOFA_TIMELAPS_MINUTES):
            self.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
            return False
        
        if self.hash_manager.generate_password_hash(code) != code_hash["code_hash"]:
            self.database_handler.add_attempts_two_factor_codes(id_two_factor_codes=code_hash["id_two_factor_codes"])
            return False
        
        self.database_handler.update_twofa_code_to_used(id_two_factor_codes=code_hash["id_two_factor_codes"])
        self.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
        return True
    
    def delete_old_code_hash(self, user_id):
        self.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)

        '''
    code_hash = database_handler.get_code_hash_from_user_id(user_id=user_id)
    if code_hash is None:
        flash("Your two-factor authentication failed. Please try again.")
        database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
        return redirect("/two_factor_authentication/")
    
    if code_hash["used"]:
        flash("This code has already been used, we have sent you a new one.")
        database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
        return redirect("/two_factor_authentication/")
    
    if code_hash["attempts"] >= 3:
        flash("Number of attempts reached, we have sent you a new code.")
        database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
        return redirect("/two_factor_authentication/")
    
    created_at = datetime.fromisoformat(code_hash["created_at"])
    if utils.datetime_is_expired_minutes(created_at, 5):
        flash("Your code has expired, we have sent you a new one.")
        database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
        return redirect("/two_factor_authentication/")
    
    if hash_manager.generate_password_hash(code) != code_hash["code_hash"]:
        flash("The code is incorrect")
        database_handler.add_attempts_two_factor_codes(id_two_factor_codes=code_hash["id_two_factor_codes"])
        return redirect("/two_factor_authentication/")
    
    database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
    database_handler.update_email_verified_from_id(user_id)
    '''
    