"""
Routes for the Emergency Information module.

URL map:
  GET  /emergency-information/               → user dashboard
  GET  /emergency-information/edit           → edit form
  POST /emergency-information/edit           → save form
  POST /emergency-information/token/regenerate → regenerate public token
  POST /emergency-information/delete         → delete record
  GET  /emergency/<token>                    → public emergency page (no auth)
  GET  /emergency-information/admin/         → admin dashboard
  POST /emergency-information/admin/<id>/toggle  → admin enable/disable
  POST /emergency-information/admin/<id>/delete  → admin delete
"""
from flask import render_template, redirect, request, flash, url_for, abort
from flask_login import login_required, current_user
from blueprints.emergency_information import bp
from blueprints.emergency_information.permissions import (
    can_edit_record, can_regenerate_token, can_delete_record
)
import extensions as ext
from utils.decorators import require_permission, require_admin

# ── User: Dashboard ───────────────────────────────────────────────────────────

@bp.route('/')
@bp.route('')
@login_required
@require_permission("emergency_information_access")
def dashboard():
    record = ext.emergency_information_service.get_record_for_user(current_user.id)
    base_url = request.host_url.rstrip('/')
    return render_template(
        'emergency_information/dashboard.html',
        id=current_user.id,
        record=record,
        base_url=base_url,
    )


# ── User: Edit ────────────────────────────────────────────────────────────────

@bp.route('/edit', methods=['GET', 'POST'])
@bp.route('/edit/', methods=['GET', 'POST'])
@login_required
@require_permission("emergency_information_access")
def edit():
    record = ext.emergency_information_service.get_record_for_user(current_user.id)

    if record and not can_edit_record(record):
        abort(403)

    if request.method == 'GET':
        return render_template(
            'emergency_information/edit.html',
            id=current_user.id,
            record=record,
            blood_types=ext.config.BLOOD_TYPES,
            gender_options=ext.config.GENDER_OPTIONS,
            relation_options=ext.config.RELATION_OPTIONS,
        )

    record, errors = ext.emergency_information_service.create_or_update_record(
        user_id=current_user.id,
        form_data=request.form,
    )

    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('emergency_information.edit'))

    flash('Your medical information has been saved successfully.', 'success')
    return redirect(url_for('emergency_information.dashboard'))


# ── User: Regenerate token ────────────────────────────────────────────────────

@bp.route('/token/regenerate', methods=['POST'])
@bp.route('/token/regenerate/', methods=['POST'])
@login_required
@require_permission("emergency_information_access")
def regenerate_token():
    record = ext.emergency_information_service.get_record_for_user(current_user.id)
    if not record:
        abort(404)
    if not can_regenerate_token(record):
        abort(403)

    ext.emergency_information_service.regenerate_token_for_record(record)
    flash('Your public emergency link has been regenerated. The previous link is now invalid.', 'success')
    return redirect(url_for('emergency_information.dashboard'))


# ── User: Delete ──────────────────────────────────────────────────────────────

@bp.route('/delete', methods=['POST'])
@bp.route('/delete/', methods=['POST'])
@login_required
@require_permission("emergency_information_access")
def delete():
    record = ext.emergency_information_service.get_record_for_user(current_user.id)
    if not record:
        abort(404)
    if not can_delete_record(record):
        abort(403)

    ext.emergency_information_service.delete_record(record)
    flash('Your emergency medical information has been deleted.', 'success')
    return redirect(url_for('emergency_information.dashboard'))


# ── Public: Token-based emergency view ───────────────────────────────────────

@bp.route('/public/<string:token>')
@bp.route('/public/<string:token>/')
def public_view(token: str):
    """
    Publicly accessible page — no authentication required.
    Intended for emergency responders scanning a QR code or receiving a link.
    """
    record = ext.emergency_information_service.get_public_record(token)
    if not record:
        abort(404)
    return render_template(
        'emergency_information/public_view.html',
        id=current_user.id,
        record=record,
    )


# ── Admin: Dashboard ──────────────────────────────────────────────────────────

@bp.route('/admin/')
@bp.route('/admin')
@login_required
@require_admin
def admin_dashboard():
    page = request.args.get('page', 1, type=int)
    pagination = ext.emergency_information_service.get_all_paginated(
        page=page,
        per_page=ext.config.ADMIN_PAGE_SIZE
    )
    return render_template(
        'emergency_information/admin_dashboard.html',
        pagination=pagination,
        records=pagination['items'],
    )


# ── Admin: Toggle active ──────────────────────────────────────────────────────

@bp.route('/admin/<int:record_id>/toggle', methods=['POST'])
@bp.route('/admin/<int:record_id>/toggle/', methods=['POST'])
@login_required
@require_admin
def admin_toggle(record_id: int):
    record = ext.emergency_information_service.get_by_id(record_id)
    if not record:
        abort(404)
    ext.emergency_information_service.set_record_active(record, not record.is_active)
    state = 'enabled' if record.is_active else 'disabled'
    flash(f'Emergency profile {state} successfully.', 'success')
    return redirect(url_for('emergency_information.admin_dashboard'))


# ── Admin: Delete ─────────────────────────────────────────────────────────────

@bp.route('/admin/<int:record_id>/delete', methods=['POST'])
@bp.route('/admin/<int:record_id>/delete/', methods=['POST'])
@login_required
@require_admin
def admin_delete(record_id: int):
    record = ext.emergency_information_service.get_by_id(record_id)
    if not record:
        abort(404)
    ext.emergency_information_service.delete_record(record)
    flash('Emergency profile deleted.', 'success')
    return redirect(url_for('emergency_information.admin_dashboard'))


# ── Admin: View single record ─────────────────────────────────────────────────

@bp.route('/admin/<int:record_id>/view')
@bp.route('/admin/<int:record_id>/view/')
@login_required
@require_admin
def admin_view(record_id: int):
    record = ext.emergency_information_service.get_by_id(record_id)
    if not record:
        abort(404)
    return render_template(
        'emergency_information/public_view.html',
        record=record,
        admin_mode=True,
    )