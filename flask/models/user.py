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
    

    def reload_data(self):
        user = self.database_handler.get_user(user_id=self.id)
        
        self.username = user["username"]
        self.name = user["name"]
        self.email = user["email"]
        self.email_verified = user["email_verified"]
        self.pay = user["pay"]
        self.role_id = user["role_id"]

        self.role_name = self.database_handler.get_role_name(role_id=self.role_id)
        self.load_permissions()
    
    ################################
    #________Permissions___________#
    ################################

    def load_permissions(self):
        self.role_name = self.database_handler.get_role_name(role_id=self.role_id)
        list_permission_id = self.database_handler.get_list_permission_id(self.role_id)
        print(list_permission_id)
        self._permissions = []
        for permission_id in list_permission_id:
            permission_name = self.database_handler.get_permission_name(permission_id=permission_id)
            self._permissions.append(permission_name)

    def has_permission(self, permission_name: str) -> bool:
        self.reload_data()
        if self._permissions is None:
            self.load_permissions()

        print("User permissions:", self._permissions)
        print("Checking:", permission_name)
        return permission_name in self._permissions