# blueprints/social_network/routes.py
# Préfixe : /social_network  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required

from blueprints.social_network import bp
from utils.decorators import require_permission
import extensions as ext


# ── Helpers internes ─────────────────────────────────────────────────────────

def _resolve_followeds(user_id: int) -> list[tuple]:
    """Retourne la liste [(id_followed, name), ...] des abonnements."""
    rows = ext.database_handler.get_all_followeds_from_id(user_id)
    return [
        (row["id_followed"], ext.database_handler.get_name_from_id(row["id_followed"]))
        for row in rows
    ]


def _resolve_followers(user_id: int) -> list[tuple]:
    """Retourne la liste [(id_follower, name), ...] des abonnés."""
    rows = ext.database_handler.get_all_followers_from_id(user_id)
    return [
        (row["id_follower"], ext.database_handler.get_name_from_id(row["id_follower"]))
        for row in rows
    ]


# ── Hub ──────────────────────────────────────────────────────────────────────

@bp.route('', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_required
def social_network_home():
    return render_template('social_network/social_network_home.html',
                           id=ext.session_manager.get_current_user_id())


# ── Amis / Abonnements ───────────────────────────────────────────────────────

@bp.route('/friends', methods=['GET', 'POST'])
@bp.route('/friends/', methods=['GET', 'POST'])
@login_required
def social_network_friends():
    user_id = ext.session_manager.get_current_user_id()

    if request.method == 'GET':
        return render_template('social_network/social_network_friends.html',
            id=user_id,
            all_followers=_resolve_followers(user_id),
            all_followeds=_resolve_followeds(user_id),
        )

    # POST : recherche d'un ami par nom
    friend_name = str(request.form.get("friend", "")).strip()
    if not friend_name:
        flash("Name is required.")
        return redirect(url_for('social_network.social_network_friends'))

    if not ext.database_handler.verif_name_exists(friend_name):
        flash("This name doesn't exist.")
        return redirect(url_for('social_network.social_network_friends'))

    id_followed = ext.database_handler.get_id_from_name(friend_name)
    return redirect(url_for('social_network.social_network_user_profile', id_account=id_followed))


@bp.route('/user_profile/<int:id_account>', methods=['GET', 'POST'])
@bp.route('/user_profile/<int:id_account>/', methods=['GET', 'POST'])
@login_required
@require_permission("view_other_profile")
def social_network_user_profile(id_account: int):
    user_id = ext.session_manager.get_current_user_id()

    # Redirection vers son propre profil si c'est soi-même
    if user_id == id_account:
        return redirect(url_for('settings.account_home'))

    id1_follow_id2 = ext.database_handler.verif_id1_follow_id2(user_id, id_account)
    return render_template('social_network/social_network_user_profile.html',
        id=user_id,
        id1_follow_id2=id1_follow_id2,
        user_profile_id=id_account,
        name=ext.database_handler.get_name_from_id(id_account),
    )


@bp.route('/follow_action/<int:id_followed>', methods=['GET', 'POST'])
@login_required
@require_permission("follow_profile")
def social_network_follow_action(id_followed: int):
    user_id = ext.session_manager.get_current_user_id()

    if id_followed == user_id:
        flash("You cannot follow yourself.")
        return redirect(url_for('social_network.social_network_friends'))

    if ext.database_handler.verif_id1_follow_id2(user_id, id_followed):
        flash("You are already following this person.")
        return redirect(url_for('social_network.social_network_friends'))

    ext.database_handler.create_link_social_network(user_id, id_followed, ext.utils.get_datetime_isoformat())
    return redirect(url_for('social_network.social_network_friends'))


@bp.route('/unfollow_action/<int:id_unfollowed>', methods=['GET', 'POST'])
@login_required
@require_permission("follow_profile")
def social_network_unfollow_action(id_unfollowed: int):
    user_id = ext.session_manager.get_current_user_id()

    if id_unfollowed == user_id:
        flash("You cannot unfollow yourself.")
        return redirect(url_for('social_network.social_network_friends'))

    ext.database_handler.delete_link_social_network_id1_id2(user_id, id_unfollowed)
    flash("You are no longer following this person.")
    return redirect(url_for('social_network.social_network_friends'))


# ── Chat privé ───────────────────────────────────────────────────────────────

@bp.route('/chat', methods=['GET', 'POST'])
@bp.route('/chat/', methods=['GET', 'POST'])
@login_required
def social_network_chat():
    user_id      = ext.session_manager.get_current_user_id()
    all_followeds = _resolve_followeds(user_id)
    return render_template('social_network/social_network_chat.html', id=user_id, all_followeds=all_followeds)


@bp.route('/chat/<int:id_receiver>', methods=['GET', 'POST'])
@bp.route('/chat/<int:id_receiver>/', methods=['GET', 'POST'])
@login_required
def social_network_chat_selected(id_receiver: int):
    user_id       = ext.session_manager.get_current_user_id()
    all_followeds = _resolve_followeds(user_id)
    messages      = ext.database_handler.get_all_messages_between_id_sender_and_receiver(user_id, id_receiver)

    return render_template('social_network/social_network_chat.html',
        id=user_id,
        all_followeds=all_followeds,
        id_receiver=id_receiver,
        messages=messages,
    )


@bp.route('/chat/send_message/<int:id_receiver>', methods=['GET', 'POST'])
@bp.route('/chat/send_message/<int:id_receiver>/', methods=['GET', 'POST'])
@login_required
@require_permission("create_own_messages")
def social_network_send_message(id_receiver: int):
    user_id = ext.session_manager.get_current_user_id()

    if request.method == 'GET':
        all_followeds = _resolve_followeds(user_id)
        messages      = ext.database_handler.get_all_messages_between_id_sender_and_receiver(user_id, id_receiver)
        return render_template('social_network/social_network_chat.html',
            id=user_id,
            all_followeds=all_followeds,
            id_receiver=id_receiver,
            messages=messages,
        )

    message = str(request.form.get('message', '')).strip()
    if not message:
        flash('Message is required.')
        return redirect(url_for('social_network.social_network_chat'))

    ext.database_handler.insert_message(user_id, id_receiver, message, ext.utils.get_datetime_isoformat())
    return redirect(url_for('social_network.social_network_chat_selected', id_receiver=id_receiver))