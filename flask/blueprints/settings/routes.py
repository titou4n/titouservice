# blueprints/settings/routes.py
# Préfixe : /settings  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for, send_file
from flask_login import login_required, current_user

from blueprints.settings import bp
from blueprints.settings.services import build_data_export, save_profile_picture
from utils.decorators import require_permission
import extensions as ext


# ── Hub settings ────────────────────────────────────────────────────────────

@bp.route('', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_required
def settings_home():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('settings/settings_home.html',
                           id=user_id,
                           name=ext.database_handler.get_name_from_id(user_id))


# ── Compte ──────────────────────────────────────────────────────────────────

@bp.route('/account', methods=['GET', 'POST'])
@bp.route('/account/', methods=['GET', 'POST'])
@login_required
@require_permission("view_own_profile")
def account_home():
    return render_template('settings/account_home.html',
                           id=current_user.id,
                           username=current_user.username,
                           name=current_user.name,
                           pay=round(current_user.pay, 2),
                           user_has_email=(current_user.email is not None),
                           email=current_user.email,
                           email_verified=current_user.email_verified,
                           role_name=current_user.role_name)


@bp.route('/account/change_email', methods=['GET', 'POST'])
@bp.route('/account/change_email/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def account_change_email():
    if request.method == 'GET':
        return render_template('settings/account_change_email.html',
                               id=current_user.id,
                               user_has_email=(current_user.email is not None),
                               email=current_user.email)

    email = str(request.form['email'])
    if not email:
        flash('Email is required !')
        return redirect(url_for('settings.account_change_email'))

    ext.database_handler.update_email_from_id(current_user.id, email)
    ext.database_handler.update_email_verified_from_id(current_user.id, False)
    flash('Your email has been updated')
    return redirect(url_for('settings.account_home'))


@bp.route('/account/change_username', methods=['GET', 'POST'])
@bp.route('/account/change_username/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def account_change_username():
    user_id = ext.session_manager.get_current_user_id()
    if request.method == 'GET':
        return render_template('settings/account_change_username.html',
                               id=user_id,
                               username=ext.database_handler.get_username_from_user_id(user_id))

    new_username = str(request.form['new_username'])
    if not new_username:
        flash('Username is required !')
        return redirect(url_for('settings.account_change_username'))

    if ext.database_handler.verif_username_exists(new_username):
        flash('This username is already taken !')
        return redirect(url_for('settings.account_change_username'))

    ext.database_handler.update_username(user_id, new_username)
    flash('Your username has been updated')
    return redirect(url_for('settings.account_home'))


@bp.route('/account/change_password', methods=['GET', 'POST'])
@bp.route('/account/change_password/', methods=['GET', 'POST'])
@login_required
@require_permission("change_own_password")
def account_change_password():
    user_id = ext.session_manager.get_current_user_id()
    if request.method == 'GET':
        return render_template('settings/account_change_password.html', id=user_id)

    actual_password    = ext.hash_manager.generate_password_hash(request.form['actual_password'])
    new_password       = ext.hash_manager.generate_password_hash(request.form['new_password'])
    verif_new_password = ext.hash_manager.generate_password_hash(request.form['verif_new_password'])

    if actual_password != ext.database_handler.get_password(user_id):
        flash('Password is not correct.')
        return redirect(url_for('settings.account_change_password'))

    if new_password != verif_new_password:
        flash("Passwords must be identical.")
        return redirect(url_for('settings.account_change_password'))

    ext.database_handler.update_password(user_id, new_password)
    flash('Your password has been updated')
    return redirect(url_for('settings.account_home'))


@bp.route('/account/change_name', methods=['GET', 'POST'])
@bp.route('/account/change_name/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def account_change_name():
    user_id = ext.session_manager.get_current_user_id()
    if request.method == 'GET':
        return render_template('settings/account_change_name.html',
                               id=user_id,
                               name=ext.database_handler.get_name_from_id(user_id))

    new_name = str(request.form['new_name'])
    if not new_name:
        flash('Name is required !')
        return redirect(url_for('settings.account_change_name'))

    if ext.database_handler.verif_name_exists(new_name):
        flash('This name is already taken !')
        return redirect(url_for('settings.account_change_name'))

    ext.database_handler.update_name(user_id, new_name)
    flash('Your name has been updated')
    return redirect(url_for('settings.account_home'))


@bp.route('/account/delete_account', methods=['GET', 'POST'])
@bp.route('/account/delete_account/', methods=['GET', 'POST'])
@login_required
@require_permission("delete_own_account")
def delete_account():
    if request.method == 'GET':
        return redirect(url_for('settings.account_home'))

    user_id = ext.session_manager.get_current_user_id()
    ext.database_handler.delete_all_post_from_id(user_id)
    ext.database_handler.delete_account(user_id)
    ext.session_manager.logout()
    flash('Your account was successfully deleted!')
    return redirect('/')


@bp.route('/account/upload_profile_picture', methods=['GET', 'POST'])
@bp.route('/account/upload_profile_picture/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def upload_profile_picture():
    if request.method == 'GET':
        return redirect(url_for('settings.account_home'))

    user_id = ext.session_manager.get_current_user_id()
    file = request.files.get('profile_picture')
    save_profile_picture(user_id, file)
    return redirect(url_for('settings.account_home'))


@bp.route('/profile_picture/<int:user_id>')
@login_required
def profile_picture(user_id: int):
    path = ext.database_handler.get_profile_picture_path_from_id(user_id)
    if not path or not __import__('os').path.isfile(path):
        path = ext.config.PATH_DEFAULT_PROFILE_PICTURE
    return send_file(path)


# ── Sécurité ─────────────────────────────────────────────────────────────────

@bp.route('/security', methods=['GET', 'POST'])
@bp.route('/security/', methods=['GET', 'POST'])
@login_required
def security_home():
    user_id = ext.session_manager.get_current_user_id()
    email   = ext.database_handler.get_email_from_id(user_id)
    sessions = ext.database_handler.get_all_sessions_from_user_id(user_id=user_id)

    return render_template('settings/security_home.html',
                           id=user_id,
                           username=ext.database_handler.get_username_from_user_id(user_id=user_id),
                           name=ext.database_handler.get_name_from_id(user_id),
                           pay=ext.database_handler.get_pay(user_id),
                           user_has_email=email is not None,
                           email=email,
                           email_verified=ext.database_handler.get_email_verified_from_id(user_id),
                           twofa_enabled=ext.database_handler.get_user_preferences_2fa(user_id=user_id),
                           session_id_hash=ext.session_manager.get_current_session_id_hash(),
                           session_location=ext.session_manager.get_location(),
                           ip_address=ext.session_manager.get_ip_session(),
                           sessions=sessions)


@bp.route('/switch_2fa', methods=['GET', 'POST'])
@bp.route('/switch_2fa/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def settings_switch_2fa():
    if request.method == 'GET':
        return redirect(url_for('settings.security_home'))

    user_id = ext.session_manager.get_current_user_id()

    if ext.database_handler.get_email_from_id(user_id) is None:
        flash("Please add an email address first.")
        return redirect(url_for('settings.account_change_email'))

    if not ext.database_handler.get_email_verified_from_id(user_id):
        flash("Please verify your email address first - Click on 'Verify-it' link.")
        return redirect(url_for('settings.security_home'))

    ext.database_handler.switch_user_preferences_2fa(user_id=user_id)
    flash('Your preferences has been updated')
    return redirect(url_for('settings.security_home'))


@bp.route('/logout_all', methods=['GET', 'POST'])
@bp.route('/logout_all/', methods=['GET', 'POST'])
@login_required
def settings_logout_all():
    user_id = ext.session_manager.get_current_user_id()
    ext.session_manager.logout_user_from_all_devices(user_id=user_id)
    return redirect('/')


@bp.route('/logout_session/<string:session_id_hash>', methods=['POST'])
@login_required
def settings_logout_session(session_id_hash: str):
    ext.session_manager.logout_session(session_id_hash=session_id_hash)
    return redirect(url_for('settings.security_home'))


@bp.route('/delete_session/<string:session_id_hash>', methods=['POST'])
@login_required
def settings_delete_session(session_id_hash: str):
    ext.session_manager.delete_session(session_id_hash=session_id_hash)
    return redirect(url_for('settings.security_home'))


# ── Notifications ────────────────────────────────────────────────────────────

@bp.route('/notifications', methods=['GET', 'POST'])
@bp.route('/notifications/', methods=['GET', 'POST'])
@login_required
def notifications_home():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('settings/notifications_home.html', id=user_id)


@bp.route('/notify_password_change', methods=['GET', 'POST'])
@bp.route('/notify_password_change/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def settings_notify_password_change():
    flash("Not Implemented")
    return redirect(url_for('settings.notifications_home'))


@bp.route('/notify_twofa_change', methods=['GET', 'POST'])
@bp.route('/notify_twofa_change/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_profile")
def settings_notify_twofa_change():
    flash("Not Implemented")
    return redirect(url_for('settings.notifications_home'))


# ── Vie privée ───────────────────────────────────────────────────────────────

@bp.route('/privacy', methods=['GET', 'POST'])
@bp.route('/privacy/', methods=['GET', 'POST'])
@login_required
def privacy_home():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('settings/privacy_home.html', id=user_id)


@bp.route('/privacy/export_data', methods=['GET', 'POST'])
@bp.route('/privacy/export_data/', methods=['GET', 'POST'])
@login_required
@require_permission("export_own_data")
def export_data():
    user_id = ext.session_manager.get_current_user_id()
    file = build_data_export(user_id)
    return send_file(file, mimetype='text/plain', as_attachment=True,
                     download_name=f'export_data_{user_id}.txt')


# ── Apparence ────────────────────────────────────────────────────────────────

@bp.route('/appearance', methods=['GET', 'POST'])
@bp.route('/appearance/', methods=['GET', 'POST'])
@login_required
def appearance_home():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('settings/appearance_home.html', id=user_id)


# ── About / Support ──────────────────────────────────────────────────────────

@bp.route('/about_support', methods=['GET', 'POST'])
@bp.route('/about_support/', methods=['GET', 'POST'])
@login_required
def about_support_home():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('settings/about_support_home.html', id=user_id)