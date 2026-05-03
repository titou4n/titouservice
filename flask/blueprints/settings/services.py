# blueprints/settings/services.py
# Logique métier settings : upload photo de profil, export des données.

import os
from io import BytesIO
from werkzeug.utils import secure_filename
from flask import current_app

import extensions as ext


def build_data_export(user_id: int) -> BytesIO:
    """Construit le fichier texte d'export des données personnelles."""
    content  = "=== PERSONALE DATA EXPORT ===\n"
    content += f"Date       : {ext.utils.format_datetime(ext.utils.get_datetime_isoformat())}\n"
    content += f"ID         : {user_id}\n"
    content += f"Username   : {ext.database_handler.get_username_from_user_id(user_id)}\n"
    content += f"Name       : {ext.database_handler.get_name_from_id(user_id)}\n"
    content += f"Pay        : {ext.database_handler.get_pay(user_id)} TC\n\n"

    metadata  = ext.database_handler.get_metadata(user_id)
    content  += "=== MÉTADONNÉES ===\n\n"
    for meta in metadata:
        content += f"{ext.utils.format_datetime(meta['date_connected'])} - IP: {meta['ipv4']}\n"

    return BytesIO(content.encode('utf-8'))


def allowed_profile_picture(filename: str) -> bool:
    allowed = current_app.config.get("ALLOWED_EXTENSIONS_PROFILE_PICTURE", set())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_profile_picture(user_id: int, file) -> bool:
    """
    Sauvegarde la photo de profil.
    Retourne True si succès, False sinon.
    """
    if not file or file.filename == '':
        return False

    if not allowed_profile_picture(file.filename):
        return False

    filename  = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    new_filename = f"user_{user_id}.{extension}"
    folder    = current_app.config['UPLOAD_PROFILE_PICTURE_FOLDER']
    filepath  = os.path.join(folder, new_filename)

    old_path = ext.database_handler.get_profile_picture_path_from_id(user_id)
    if old_path and os.path.exists(old_path):
        os.remove(old_path)

    file.save(filepath)
    ext.database_handler.update_profile_picture_path_from_id(user_id, filepath)
    return True