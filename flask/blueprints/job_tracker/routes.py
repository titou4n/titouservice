from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from datetime import date, datetime
import extensions as ext

from models.candidature import STATUTS, STATUT_COLORS
from blueprints.job_tracker import bp

candidatures_bp = Blueprint("candidatures", __name__)
dashboard_bp    = Blueprint("dashboard",    __name__)
entreprises_bp  = Blueprint("entreprises",  __name__)
statistiques_bp = Blueprint("statistiques", __name__)

bp.register_blueprint(candidatures_bp, url_prefix="/candidatures")
bp.register_blueprint(dashboard_bp,    url_prefix="/dashboard")
bp.register_blueprint(entreprises_bp,  url_prefix="/entreprises")
bp.register_blueprint(statistiques_bp, url_prefix="/statistiques")


# ==============================================================================
# Candidatures
# ==============================================================================

@candidatures_bp.route("/")
@login_required
def index():
    candidatures = ext.database_job_tracker.get_all_candidatures(user_id=current_user.id)
    entreprises  = ext.database_job_tracker.get_all_entreprises(user_id=current_user.id)

    kanban = {s: [] for s in STATUTS}
    for c in candidatures:
        if c["status"] in kanban:
            kanban[c["status"]].append(c)

    return render_template(
        "job_tracker/job_tracker_candidatures.html",
        kanban=kanban,
        statuts=STATUTS,
        entreprises=entreprises,
        active="candidatures",
        id=current_user.id,
    )


@candidatures_bp.route("/ajouter", methods=["POST"])
@login_required
def ajouter():
    title            = request.form.get("title", "").strip()
    company_id       = request.form.get("company_id") or None
    status           = request.form.get("status", "À postuler")
    notes            = request.form.get("notes", "").strip()
    date_applied_str = request.form.get("date_applied")

    if not title:
        flash("Le titre est obligatoire.", "error")
        return redirect(url_for("job_tracker.candidatures.index"))

    date_applied = date.today()
    if date_applied_str:
        try:
            date_applied = date.fromisoformat(date_applied_str)
        except ValueError:
            pass

    ext.database_job_tracker.add_candidature(
        title=title,
        company_id=int(company_id) if company_id else None,
        status=status,
        date_applied=date_applied,
        notes=notes,
        user_id=current_user.id,
    )
    flash("Candidature ajoutée !", "success")
    return redirect(url_for("job_tracker.candidatures.index"))


@candidatures_bp.route("/<int:id>/modifier", methods=["POST"])
@login_required
def modifier(id):
    c = ext.database_job_tracker.get_candidature(id)
    if c is None:
        flash("Candidature introuvable.", "error")
        return redirect(url_for("job_tracker.candidatures.index"))

    title            = request.form.get("title", c["title"]).strip()
    company_id       = request.form.get("company_id") or None
    status           = request.form.get("status", c["status"])
    notes            = request.form.get("notes", c["notes"])
    date_applied_str = request.form.get("date_applied")

    date_applied = date.fromisoformat(c["date_applied"]) if c["date_applied"] else date.today()
    if date_applied_str:
        try:
            date_applied = date.fromisoformat(date_applied_str)
        except ValueError:
            pass

    ext.database_job_tracker.update_candidature(
        id=id,
        title=title,
        company_id=int(company_id) if company_id else None,
        status=status,
        date_applied=date_applied,
        notes=notes,
    )
    flash("Candidature mise à jour.", "success")
    return redirect(url_for("job_tracker.candidatures.index"))


@candidatures_bp.route("/<int:id>/supprimer", methods=["POST"])
@login_required
def supprimer(id):
    c = ext.database_job_tracker.get_candidature(id)
    if c is None:
        flash("Candidature introuvable.", "error")
        return redirect(url_for("job_tracker.candidatures.index"))

    ext.database_job_tracker.delete_candidature(id)
    flash("Candidature supprimée.", "info")
    return redirect(url_for("job_tracker.candidatures.index"))


@candidatures_bp.route("/<int:id>/statut", methods=["POST"])
@login_required
def changer_statut(id):
    """Endpoint AJAX pour drag & drop kanban."""
    data       = request.get_json()
    new_status = data.get("status")

    if new_status not in STATUTS:
        return jsonify({"success": False, "error": "Statut invalide"}), 400

    c = ext.database_job_tracker.update_statut(id, new_status)
    if c is None:
        return jsonify({"success": False, "error": "Candidature introuvable"}), 404

    return jsonify({"success": True, "status": c["status"]})


@candidatures_bp.route("/api/all")
@login_required
def api_all():
    candidatures = ext.database_job_tracker.get_all_candidatures(user_id=current_user.id)
    return jsonify(candidatures)


# ==============================================================================
# Dashboard
# ==============================================================================

@dashboard_bp.route("/")
@login_required
def dashboard():
    uid = current_user.id

    total          = ext.database_job_tracker.count_total(user_id=uid)
    by_status      = ext.database_job_tracker.count_by_status(user_id=uid)
    recentes       = ext.database_job_tracker.get_recentes(user_id=uid, limit=5)
    nb_entreprises = ext.database_job_tracker.count_entreprises(user_id=uid)

    entreprises  = ext.database_job_tracker.get_all_entreprises(user_id=current_user.id)

    by_status_full = {s: by_status.get(s, 0) for s in STATUTS}

    for app in recentes:
        try:
            if isinstance(app["date_applied"], str) and app["date_applied"]:
                app["date_applied"] = datetime.fromisoformat(app["date_applied"]).strftime("%d/%m/%Y")
        except Exception:
            pass

    return render_template(
        "job_tracker/job_tracker_dashboard.html",
        total=total,
        by_status=by_status_full,
        recentes=recentes,
        nb_entreprises=nb_entreprises,
        statuts=STATUTS,
        entreprises=entreprises,
        active="dashboard",
        id=uid,
    )


# ==============================================================================
# Entreprises
# ==============================================================================

@entreprises_bp.route("/")
@login_required
def index():
    entreprises = ext.database_job_tracker.get_all_entreprises(user_id=current_user.id)
    return render_template(
        "job_tracker/job_tracker_entreprises.html",
        entreprises=entreprises,
        active="entreprises",
        id=current_user.id,
    )


@entreprises_bp.route("/ajouter", methods=["POST"])
@login_required
def ajouter():
    name = request.form.get("name", "").strip()

    if not name:
        flash("Le nom est obligatoire.", "error")
        return redirect(url_for("job_tracker.entreprises.index"))

    ext.database_job_tracker.add_entreprise(
        name=name,
        secteur=request.form.get("secteur", "").strip(),
        localisation=request.form.get("localisation", "").strip(),
        notes=request.form.get("notes", "").strip(),
        user_id=current_user.id,
    )
    flash("Entreprise ajoutée !", "success")
    return redirect(url_for("job_tracker.entreprises.index"))


@entreprises_bp.route("/<int:id>/modifier", methods=["POST"])
@login_required
def modifier(id):
    e = ext.database_job_tracker.get_entreprise(id)
    if e is None:
        flash("Entreprise introuvable.", "error")
        return redirect(url_for("job_tracker.entreprises.index"))

    ext.database_job_tracker.update_entreprise(
        id=id,
        name=request.form.get("name", e["name"]).strip(),
        secteur=request.form.get("secteur", e["secteur"]),
        localisation=request.form.get("localisation", e["localisation"]),
        notes=request.form.get("notes", e["notes"]),
    )
    flash("Entreprise mise à jour.", "success")
    return redirect(url_for("job_tracker.entreprises.index"))


@entreprises_bp.route("/<int:id>/supprimer", methods=["POST"])
@login_required
def supprimer(id):
    e = ext.database_job_tracker.get_entreprise(id)
    if e is None:
        flash("Entreprise introuvable.", "error")
        return redirect(url_for("job_tracker.entreprises.index"))

    ext.database_job_tracker.delete_entreprise(id)
    flash("Entreprise supprimée.", "info")
    return redirect(url_for("job_tracker.entreprises.index"))


@entreprises_bp.route("/<int:id>")
@login_required
def detail(id):
    e = ext.database_job_tracker.get_entreprise(id)
    if e is None:
        flash("Entreprise introuvable.", "error")
        return redirect(url_for("job_tracker.entreprises.index"))

    return render_template(
        "job_tracker/job_tracker_entreprise_detail.html",
        entreprise=e,
        active="entreprises",
    )


# ==============================================================================
# Statistiques
# ==============================================================================

@statistiques_bp.route("/")
@login_required
def index():
    uid = current_user.id

    # FIX #7 : passage du user_id
    by_status       = ext.database_job_tracker.count_by_status(user_id=uid)
    top_entreprises = ext.database_job_tracker.top_entreprises(user_id=uid, limit=5)
    total           = ext.database_job_tracker.count_total(user_id=uid)

    by_status_full = {s: by_status.get(s, 0) for s in STATUTS}

    # top_entreprises est une liste de dicts {"name": ..., "nb": ...}
    # On conserve le format tuple attendu par le template : (name, nb)
    top_entreprises_tuples = [(e["name"], e["nb"]) for e in top_entreprises]

    return render_template(
        "job_tracker/job_tracker_statistiques.html",
        by_status=by_status_full,
        top_entreprises=top_entreprises_tuples,
        statuts=STATUTS,
        colors=STATUT_COLORS,
        total=total,
        active="statistiques",
    )


@statistiques_bp.route("/api/data")
@login_required
def api_data():
    """JSON pour Chart.js."""
    uid = current_user.id

    by_status       = ext.database_job_tracker.count_by_status(user_id=uid)
    top_entreprises = ext.database_job_tracker.top_entreprises(user_id=uid, limit=6)

    by_status_full = {s: by_status.get(s, 0) for s in STATUTS}

    return jsonify({
        "statuts": {
            "labels": list(by_status_full.keys()),
            "data":   list(by_status_full.values()),
            "colors": [STATUT_COLORS.get(s, "#64748b") for s in by_status_full],
        },
        "entreprises": {
            "labels": [e["name"] for e in top_entreprises],
            "data":   [e["nb"]   for e in top_entreprises],
        },
    })