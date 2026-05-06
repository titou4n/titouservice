# utils/decorators.py
# Decorators that can be reused by all blueprints.

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


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