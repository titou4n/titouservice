# blueprints/chatroom/routes.py
# Préfixe : /chatroom  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for, abort
from flask_login import login_required, current_user

from blueprints.chatroom import bp
from utils.decorators import require_permission
import extensions as ext


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@login_required
@require_permission("view_content")
def chatroom():

    posts   = ext.db_post_repository.get_all()
    names = {
        post["user_id"]: ext.db_account_repository.get_name_by_id(post["user_id"])
        for post in posts
    }

    return render_template('chatroom/chatroom_home.html', id=current_user.id, posts=posts, names=names)


@bp.route('/create_post', methods=['GET', 'POST'])
@bp.route('/create_post/', methods=['GET', 'POST'])
@login_required
@require_permission("create_content")
def create_post():

    if request.method == 'GET':
        return render_template('chatroom/chatroom_create_post.html', id=current_user.id)

    title   = str(request.form['title'])
    content = str(request.form['content'])

    if not title or not content:
        flash('Error: Title and Content are required.')
        return redirect(url_for('chatroom.create_post'))

    ext.db_post_repository.create(current_user.id, title, content)
    return redirect(url_for('chatroom.chatroom'))


@bp.route('/edit_post/<int:id_post>', methods=['GET', 'POST'])
@bp.route('/edit_post/<int:id_post>/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_content")
def edit_post(id_post: int):
    
    # Vérification de propriété
    if current_user.id != ext.db_post_repository.get_user_id_by_post_id(id_post):
        flash("You cannot edit this post.")
        return redirect(url_for('chatroom.chatroom'))

    if request.method == 'GET':
        post = ext.db_post_repository.get_by_id(id_post)
        return render_template('chatroom/chatroom_edit_post.html', id=current_user.id, post=post)

    title   = str(request.form['title'])
    content = str(request.form['content'])

    if not title or not content:
        flash('Error: Title and Content are required.')
        return redirect(url_for('chatroom.edit_post', id_post=id_post))

    ext.db_post_repository.update(id_post, title, content)
    return redirect(url_for('chatroom.chatroom'))


@bp.route('/delete/<int:id_post>', methods=['POST'])
@bp.route('/delete/<int:id_post>/', methods=['POST'])
@login_required
@require_permission("delete_own_content")
def delete_post(id_post: int):
    owner_id = ext.db_post_repository.get_user_id_by_post_id(id_post)
    if owner_id is None:
        abort(404)

    # Vérification de propriété (les modérateurs/admins avec "delete_all_content" restent autorisés)
    if owner_id != current_user.id and not current_user.has_permission("delete_all_content"):
        abort(403)

    post = ext.db_post_repository.get_by_id(id_post)
    ext.db_post_repository.delete(id_post)
    flash(f'"{post["title"]}" was successfully deleted!')
    return redirect(url_for('chatroom.chatroom'))
