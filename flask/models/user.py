from flask_login import UserMixin
from Data.database_handler import DatabaseHandler
from utils.utils import Utils
from config import Config

class User(UserMixin):
    def __init__(self, user_id:int):
        # init object
        self.database_handler = DatabaseHandler()
        self.config = Config()
        self.utils = Utils()

        # init parameters
        user = self.database_handler.get_user(user_id=user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")
        
        self.id = user_id
        self.username = user["username"]
        self.name = user["name"]
        self.email = user["email"]
        self.email_verified = user["email_verified"]
        self.pay = user["pay"]
        self.role_id = user["role_id"]

        self.role_name = self.database_handler.get_role_name(role_id=self.role_id)
        self._permissions = None

    ###############################
    #_________Flask-Login_________#
    ###############################

    # is_authenticated()
    # is_anonymous()
    # is_active()

    def get_id(self):
        return str(self.id)
    
    
    ################################
    #________Permissions___________#
    ################################

    def load_permissions(self):
        permissions = self.database_handler.get_permissions_name(self.id)

        if permissions is None:
            self._permissions = []
        else:
            self._permissions = permissions

    def has_permission(self, permission_name: str) -> bool:
        if self._permissions is None:
            self.load_permissions()

        return permission_name in self._permissions

