# utils/decorators.py
# Decorators that can be reused by all blueprints.

from functools import wraps
from flask import flash, redirect, url_for,abort
from flask_login import current_user
import extensions as ext

def require_login(f):
    """Redirect to 401 if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)
    return decorated

def require_permission(permission_name: str):
    """Check that a logged-in user has the requested permission."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))

            if not current_user.has_permission(permission_name):
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("main.home"))

            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin(f):
    """Abort with 403 if the user is not an admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ext.permission_manager.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated