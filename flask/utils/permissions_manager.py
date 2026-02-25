from Data.database_handler import DatabaseHandler
from utils.utils import Utils
from config import Config

class PermissionsManager():
    def __init__(self):
        self.database_handler = DatabaseHandler()
        self.config = Config()
        self.utils = Utils()

    def get_dict(self):
        permissions_dict = {}

        query = self.database_handler.get_all_couple_role_and_permissions_id()
        for role_id, permission_id in query:

            role_name = self.database_handler.get_role_name(role_id)
            permission_name = self.database_handler.get_permission_name(permission_id)

            if role_name in permissions_dict.keys():
                permissions_dict[role_name].append(permission_name)
            else:
                permissions_dict[role_name] = [permission_name]

        return permissions_dict
    
    def create_role(self, role_name:str, list_permission:list) -> None:
        
        if role_name is None or role_name == "":
            raise RoleNameError
        
        if list_permission is None:
            raise ListPermissionError
        
        self.database_handler.insert_role(role_name=role_name)
        self.database_handler.get_role_id(role_name=role_name)

    def delete_role(self, role_id:int):

        self.database_handler.delete_role_from_role_permission(role_id=role_id)
        self.database_handler.delete_role(role_id=role_id)
        

        
    


class PermissionsManagerError(Exception):
    pass

class RoleNameError(PermissionsManagerError):
    pass

class ListPermissionError(PermissionsManagerError):
    pass