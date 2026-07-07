# blueprints/social_network/routes.py
# Préfixe : /social_network  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user

from blueprints.social_network import bp
from utils.decorators import require_permission
import extensions as ext


# ── Helpers internes ─────────────────────────────────────────────────────────

def _resolve_followeds(user_id: int) -> list[tuple]:
    """Retourne la liste [(id_followed, name), ...] des abonnements."""
    rows = ext.db_social_repository.get_followings(user_id)
    return [
        (row["followed_id"], ext.db_account_repository.get_name_by_id(row["followed_id"]))
        for row in rows
    ]


def _resolve_followers(user_id: int) -> list[tuple]:
    """Retourne la liste [(id_follower, name), ...] des abonnés."""
    rows = ext.db_social_repository.get_followers(user_id)
    return [
        (row["follower_id"], ext.db_account_repository.get_name_by_id(row["follower_id"]))
        for row in rows
    ]


# ── Hub ──────────────────────────────────────────────────────────────────────

@bp.route('', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_required
def social_network_home():
    return render_template('social_network/social_network_home.html',
                           id=current_user.id)


# ── Amis / Abonnements ───────────────────────────────────────────────────────

@bp.route('/friends', methods=['GET', 'POST'])
@bp.route('/friends/', methods=['GET', 'POST'])
@login_required
def social_network_friends():
    if request.method == 'GET':
        return render_template('social_network/social_network_friends.html',
            id=current_user.id,
            all_followers=_resolve_followers(current_user.id),
            all_followeds=_resolve_followeds(current_user.id),
        )

    # POST : recherche d'un ami par nom
    friend_name = str(request.form.get("friend", "")).strip()
    if not friend_name:
        flash("Name is required.")
        return redirect(url_for('social_network.social_network_friends'))

    if not ext.db_account_repository.exists_by_name(friend_name):
        flash("This name doesn't exist.")
        return redirect(url_for('social_network.social_network_friends'))

    id_followed = ext.db_account_repository.get_id_by_name(friend_name)
    return redirect(url_for('social_network.social_network_user_profile', id_account=id_followed))


@bp.route('/user_profile/<int:id_account>', methods=['GET', 'POST'])
@bp.route('/user_profile/<int:id_account>/', methods=['GET', 'POST'])
@login_required
@require_permission("view_other_profile")
def social_network_user_profile(id_account: int):
    # Redirection vers son propre profil si c'est soi-même
    if current_user.id == id_account:
        return redirect(url_for('settings.account_home'))

    id1_follow_id2 = ext.db_social_repository.is_following(current_user.id, id_account)
    return render_template('social_network/social_network_user_profile.html',
        id=current_user.id,
        id1_follow_id2=id1_follow_id2,
        user_profile_id=id_account,
        name=ext.db_account_repository.get_name_by_id(id_account),
    )


@bp.route('/follow_action/<int:id_followed>', methods=['POST'])
@login_required
@require_permission("follow_profile")
def social_network_follow_action(id_followed: int):
    if id_followed == current_user.id:
        flash("You cannot follow yourself.")
        return redirect(url_for('social_network.social_network_friends'))

    if ext.db_social_repository.is_following(current_user.id, id_followed):
        flash("You are already following this person.")
        return redirect(url_for('social_network.social_network_friends'))

    ext.db_social_repository.follow(current_user.id, id_followed, ext.utils.get_datetime_isoformat())
    return redirect(url_for('social_network.social_network_friends'))


@bp.route('/unfollow_action/<int:id_unfollowed>', methods=['POST'])
@login_required
@require_permission("follow_profile")
def social_network_unfollow_action(id_unfollowed: int):
    if id_unfollowed == current_user.id:
        flash("You cannot unfollow yourself.")
        return redirect(url_for('social_network.social_network_friends'))

    ext.db_social_repository.unfollow(current_user.id, id_unfollowed)
    flash("You are no longer following this person.")
    return redirect(url_for('social_network.social_network_friends'))


# ── Chat privé ───────────────────────────────────────────────────────────────

@bp.route('/chat', methods=['GET', 'POST'])
@bp.route('/chat/', methods=['GET', 'POST'])
@login_required
def social_network_chat():
    all_followeds = _resolve_followeds(current_user.id)
    return render_template('social_network/social_network_chat.html', id=current_user.id, all_followeds=all_followeds)


@bp.route('/chat/<int:id_receiver>', methods=['GET', 'POST'])
@bp.route('/chat/<int:id_receiver>/', methods=['GET', 'POST'])
@login_required
def social_network_chat_selected(id_receiver: int):
    if not ext.db_social_repository.is_following(current_user.id, id_receiver):
        flash("You can only message accounts you follow.")
        return redirect(url_for('social_network.social_network_chat'))

    all_followeds = _resolve_followeds(current_user.id)
    messages      = ext.db_social_repository.get_conversation(current_user.id, id_receiver)

    return render_template('social_network/social_network_chat.html',
        id=current_user.id,
        all_followeds=all_followeds,
        id_receiver=id_receiver,
        messages=messages,
    )


@bp.route('/chat/send_message/<int:id_receiver>', methods=['GET', 'POST'])
@bp.route('/chat/send_message/<int:id_receiver>/', methods=['GET', 'POST'])
@login_required
@require_permission("create_messages")
def social_network_send_message(id_receiver: int):
    if not ext.db_social_repository.is_following(current_user.id, id_receiver):
        flash("You can only message accounts you follow.")
        return redirect(url_for('social_network.social_network_chat'))

    if request.method == 'GET':
        all_followeds = _resolve_followeds(current_user.id)
        messages      = ext.db_social_repository.get_conversation(current_user.id, id_receiver)
        return render_template('social_network/social_network_chat.html',
            id=current_user.id,
            all_followeds=all_followeds,
            id_receiver=id_receiver,
            messages=messages,
        )

    message = str(request.form.get('message', '')).strip()
    if not message:
        flash('Message is required.')
        return redirect(url_for('social_network.social_network_chat'))

    ext.db_social_repository.send_message(current_user.id, id_receiver, message, ext.utils.get_datetime_isoformat())
    return redirect(url_for('social_network.social_network_chat_selected', id_receiver=id_receiver))
