# blueprints/auth/services.py
# Logique métier auth : isolée des routes pour faciliter les tests.

import extensions as ext
from models.user import User
from flask_login import login_user


def authenticate_user(username: str, raw_password: str):
    """
    Authentifie un utilisateur.
    Retourne (user_id, error_message).
    error_message est None si succès.
    """
    password = ext.hash_manager.generate_password_hash(raw_password)

    if not username:
        return None, "Username is required."

    user_id = ext.database_handler.get_id_from_username(username)
    if user_id is None:
        return None, "Username is not correct."

    if password != ext.database_handler.get_password(user_id):
        return None, "Password is not correct."

    return user_id, None


def register_user(username: str, raw_password: str, raw_verif: str, name: str):
    """
    Crée un compte.
    Retourne (user_id, error_message).
    """
    password = ext.hash_manager.generate_password_hash(raw_password)
    verif    = ext.hash_manager.generate_password_hash(raw_verif)

    if ext.database_handler.verif_username_exists(username):
        return None, "Username is already used."

    if ext.database_handler.verif_name_exists(name):
        return None, "Name is already used."

    if password != verif:
        return None, "Passwords must be identical."

    role_id = ext.database_handler.get_role_id(role_name="user")
    ext.database_handler.create_account(username, password, name, role_id)
    user_id = ext.database_handler.get_id_from_username(username)

    ext.session_manager.send_session(user_id=user_id)
    ext.database_handler.insert_user_preferences(user_id=user_id)

    user = User(user_id)
    login_user(user)
    ext.session_manager.insert_metadata()

    return user_id, None


def login_as_visitor():
    """
    Authentifie le compte visiteur pré-configuré.
    Retourne (user_id, error_message).
    """
    username = ext.config.USERNAME_VISITOR
    password = ext.hash_manager.generate_password_hash(ext.config.PASSWORD_VISITOR)

    user_id = ext.database_handler.get_id_from_username(username)
    if user_id is None:
        return None, "Visitor account not found."

    if password != ext.database_handler.get_password(user_id):
        return None, "Visitor account misconfigured."

    ext.session_manager.send_session(user_id=user_id)
    user = User(user_id)
    login_user(user)
    return user_id, None