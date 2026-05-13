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
    if not username:
        return None, "Username is required."

    user_id = ext.db_account_repository.get_id_by_username(username)
    if user_id is None:
        return None, "Username is not correct."

    stored_hash = ext.db_account_repository.get_password_hash(user_id)
    if not ext.hash_manager.check_password(raw_password, stored_hash):
        return None, "Password is not correct."
    
    ext.db_account_repository.insert_metadata(
        user_id=user_id,
        date_connected=ext.utils.get_datetime_isoformat(),
        ipv4="0.0.0.0"
    )

    return user_id, None


def register_user(username: str, raw_password: str, raw_verif: str, name: str):
    """
    Crée un compte.
    Retourne (user_id, error_message).
    """
    if ext.db_account_repository.exists_by_username(username):
        return None, "Username is already used."

    if ext.db_account_repository.exists_by_name(name):
        return None, "Name is already used."

    if raw_password != raw_verif:
        return None, "Passwords must be identical."

    password_hash = ext.hash_manager.generate_password_hash(raw_password)
    role_id       = ext.db_role_repository.get_role_id(role_name="user")
    ext.db_account_repository.create(username, password_hash, name, role_id)

    user_id = ext.db_account_repository.get_id_by_username(username)

    ext.session_manager.send_session(user_id=user_id)
    ext.db_account_repository.create_preferences(user_id=user_id)

    user = User(user_id)
    login_user(user)

    ext.db_account_repository.insert_metadata(
        user_id=user_id,
        date_connected=ext.utils.get_datetime_isoformat(),
        ipv4="0.0.0.0"
    )

    return user_id, None


def login_as_visitor():
    """
    Authentifie le compte visiteur pré-configuré.
    Retourne (user_id, error_message).
    """
    username = ext.config.USERNAME_VISITOR

    user_id = ext.db_account_repository.get_id_by_username(username)
    if user_id is None:
        return None, "Visitor account not found."

    stored_hash = ext.db_account_repository.get_password_hash(user_id)
    if not ext.hash_manager.check_password(ext.config.PASSWORD_VISITOR, stored_hash):
        return None, "Visitor account misconfigured."

    ext.session_manager.send_session(user_id=user_id)
    user = User(user_id)
    login_user(user)

    ext.db_account_repository.insert_metadata(
        user_id=user_id,
        date_connected=ext.utils.get_datetime_isoformat(),
        ipv4="0.0.0.0"
    )

    return user_id, None
