# blueprints/auth/routes.py

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user

from blueprints.auth import bp
from blueprints.auth.services import authenticate_user, register_user, login_as_visitor
import extensions as ext
from models.user import User
from flask_login import login_user
from utils.twofa_manager import (
    TwoFactorCodeNotFoundError, TwoFactorCodeAlreadyUsedError,
    TwoFactorTooManyAttemptsError, TwoFactorCodeExpiredError,
    TwoFactorInvalidCodeError
)


@bp.route('/login', methods=['GET', 'POST'])
@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    username = str(request.form['username'])
    raw_password = str(request.form['password'])

    user_id, error = authenticate_user(username, raw_password)
    if error:
        flash(error)
        return redirect(url_for('auth.login'))

    ext.session_manager.send_session(user_id=user_id)

    if ext.database_handler.get_user_preferences_2fa(user_id=user_id):
        return redirect('/two_factor_authentication/')

    user = User(user_id)
    login_user(user)
    ext.session_manager.insert_metadata()
    return redirect('/home/')


@bp.route('/register', methods=['GET', 'POST'])
@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')

    user_id, error = register_user(
        username=str(request.form['username']),
        raw_password=str(request.form['password']),
        raw_verif=str(request.form['verif_password']),
        name=str(request.form['name'])
    )
    if error:
        flash(error)
        return redirect(url_for('auth.register'))

    return redirect('/home/')


@bp.route('/visitor', methods=['GET', 'POST'])
@bp.route('/visitor/', methods=['GET', 'POST'])
def continue_as_a_visitor():
    user_id, error = login_as_visitor()
    if error:
        flash(error)
        return render_template('auth/login.html')
    return redirect('/home/')


@bp.route('/forgot_password', methods=['GET', 'POST'])
@bp.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    if ext.session_manager.get_current_user_id() is not None:
        ext.session_manager.insert_metadata()
        return redirect('/home/')

    if request.method == 'GET':
        return render_template('auth/forgot_password.html')

    username = str(request.form['username'])
    if not username:
        flash('Username is required.')
        return render_template('auth/login.html')

    user_id = ext.database_handler.get_id_from_username(username)
    if user_id is None:
        flash("Username doesn't exist.")
        return render_template('auth/login.html')

    user_email = ext.database_handler.get_email_from_id(user_id)
    if user_email is None:
        flash("No email has been added.")
        return render_template('auth/login.html')

    if not ext.database_handler.get_email_verified_from_id(user_id):
        flash("No email has been verified.")
        return render_template('auth/login.html')

    new_password = ext.utils.generate_password(size=20)
    ext.database_handler.update_password(
        user_id,
        new_password=ext.hash_manager.generate_password_hash(new_password)
    )
    ext.email_manager.send_new_password_code_with_html(user_id=user_id, new_password=new_password)
    flash(f"An email containing a new password has been sent to "
          f"{ext.email_manager.get_hide_email(user_id=user_id)}.")
    return redirect(url_for('auth.login'))


@bp.route('/two_factor_authentication', methods=['GET', 'POST'])
@bp.route('/two_factor_authentication/', methods=['GET', 'POST'])
@login_required
def two_factor_authentication():
    user_id = ext.session_manager.get_current_user_id()
    ext.database_handler.delete_old_code_hash()

    if request.method == 'GET':
        if ext.twofa_manager.verif_need_to_sent_new_code(user_id=user_id):
            ext.database_handler.delete_old_code_hash_from_user_id(user_id=user_id)
            ext.twofa_manager.send_code(user_id=user_id)
        flash(f"An email containing a two-factor authentication code has been sent to: "
              f"{ext.email_manager.get_hide_email(user_id=user_id)}")
        return render_template('auth/two_factor_authentication.html')

    code = str(request.form['code'])
    try:
        ext.twofa_manager.verif_code(code, user_id)
        flash("Your two-factor authentication sucess.")

        if current_user.email == ext.config.EMAIL_ADDRESS:
            role_id = ext.database_handler.get_role_id(role_name=ext.config.ROLE_NAME_SUPER_ADMIN)
            ext.database_handler.update_user_role(user_id=current_user.id, role_id=role_id)
            flash("You are now a super administrator.")
            return redirect(url_for("admin.admin_panel"))

        return redirect(url_for("main.home"))

    except TwoFactorCodeNotFoundError:
        flash("No authentication code found.", "error")
    except TwoFactorCodeAlreadyUsedError:
        flash("This code was already used.", "error")
    except TwoFactorTooManyAttemptsError:
        flash("Too many attempts. Request a new code.", "error")
    except TwoFactorCodeExpiredError:
        flash("Code expired. Request a new one.", "error")
    except TwoFactorInvalidCodeError:
        flash("Invalid code.", "error")

    return redirect(url_for("auth.two_factor_authentication"))