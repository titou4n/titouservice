# blueprints/main/routes.py

import io
from flask import render_template, redirect, send_file, url_for
from flask_login import login_required, current_user, logout_user

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
        import logging
        logging.getLogger(__name__).error("Graph error: %s", e)
        return "", 204


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('main/index.html')


@bp.route('/home')
@bp.route('/home/')
@login_required
def home():
    return render_template('main/home.html',
        id=current_user.id,
        name=ext.db_account_repository.get_name_by_id(current_user.id),
        access_admin_panel=current_user.has_permission("access_admin_panel")
    )


@bp.route('/logout')
@bp.route('/logout/')
@login_required
def logout():
    logout_user()
    ext.session_manager.logout()
    return redirect('/')


@bp.route('/conditions_uses')
@bp.route('/conditions_uses/')
def conditions_uses():
    return render_template('main/conditions_uses.html')


@bp.route('/thank_you')
@bp.route('/thank_you/')
def thank_you():
    return render_template('main/thank_you.html')
