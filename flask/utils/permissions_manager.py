import extensions as ext
from utils.utils import Utils

class PermissionsManager():
    def __init__(self):
        self.db_account = ext.db_account_repository
        self.db_role = ext.db_role_repository
        self.config = ext.config
        self.utils = Utils()

    def get_dict(self) -> dict[str, list[str]]:
        permissions_dict: dict[str, list[str]] = {}

        list_all_role: list[dict] = self.db_role.get_all_roles()
        for role in list_all_role:
            role_name: str = role["name"]
            permissions_dict[role_name] = []

        query: list[tuple[int, int]] = self.db_role.get_all_role_permission_pairs()
        for role_id, permission_id in query:

            role_name: str = self.db_role.get_role_name(role_id)
            permission_name: str = self.db_role.get_permission_name(permission_id)

            if role_name in permissions_dict.keys():
                permissions_dict[role_name].append(permission_name)
            else:
                permissions_dict[role_name] = [permission_name]

        return permissions_dict
    
    def create_role(self, role_name:str, list_permissions:list) -> None:
        
        if role_name is None or role_name == "":
            raise RoleNameError
    
        if self.db_role.role_exists(role_name):
            raise RoleNameError
        
        if list_permissions is None:
            raise ListPermissionError
        
        self.db_role.insert_role(role_name=role_name)
        role_id = self.db_role.get_role_id(role_name=role_name)

        # Add permissions
        for permission_name in list_permissions:
            permission_id = self.db_role.get_permission_id(permission_name=permission_name)
            self.db_role.insert_role_permission(role_id=role_id, permission_id=permission_id)

    def edit_role(self, role_id:int, new_role_name:str, list_permissions:list) -> None:
        
        if new_role_name is None or new_role_name == "":
            raise RoleNameError
        
        if self.db_role.role_exists(new_role_name):
            raise RoleNameError
        
        if list_permissions is None:
            raise ListPermissionError
        
        self.db_role.update_role(role_id=role_id, role_name=new_role_name)
        self.db_role.delete_permissions_for_role(role_id=role_id)

        # Add permissions
        for permission_name in list_permissions:
            permission_id = self.db_role.get_permission_id(permission_name=permission_name)
            self.db_role.insert_role_permission(role_id=role_id, permission_id=permission_id)

    def delete_role(self, role_id:int):
        self.db_role.delete_permissions_for_role(role_id=role_id)
        self.db_role.delete_role(role_id=role_id)
        

class PermissionsManagerError(Exception):
    pass

class RoleNameError(PermissionsManagerError):
    pass

class ListPermissionError(PermissionsManagerError):
    pass