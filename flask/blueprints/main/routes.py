# blueprints/main/routes.py

import io
from flask import render_template, redirect, send_file
from flask_login import login_required, current_user

from blueprints.main import bp
import extensions as ext


@bp.route('/graph/connections-per-day')
def get_graph_connection_per_day():
    buffer = io.BytesIO()
    try:
        ext.view_data.get_graph_connection_per_day(
            type_graph="stackplot",
            output_path=buffer
        )
        buffer.seek(0)
        return send_file(buffer, mimetype="image/png")
    except Exception as e:
        print(f"[TITOUSERVICE - ERROR] Graph : {e}")
        return "", 204


@bp.route('/')
def index():
    if ext.session_manager.get_current_user_id() is None:
        return render_template('main/index.html')
    ext.session_manager.insert_metadata()
    return redirect('/home/')


@bp.route('/home')
@bp.route('/home/')
@login_required
def home():
    return render_template('main/home.html',
        id=current_user.id,
        name=ext.database_handler.get_name_from_id(current_user.id),
        access_admin_panel=current_user.has_permission("access_admin_panel")
    )


@bp.route('/logout')
@bp.route('/logout/')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    ext.session_manager.logout()
    return redirect('/')


@bp.route('/conditions_uses')
@bp.route('/conditions_uses/')
def conditions_uses():
    return render_template('main/conditions_uses.html', id=ext.session_manager.get_current_user_id())


@bp.route('/thank_you')
@bp.route('/thank_you/')
def thank_you():
    return render_template('main/thank_you.html', id=ext.session_manager.get_current_user_id())