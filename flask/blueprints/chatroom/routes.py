# blueprints/chatroom/routes.py
# Préfixe : /chatroom  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required

from blueprints.chatroom import bp
from utils.decorators import require_permission
import extensions as ext


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@login_required
@require_permission("view_content")
def chatroom():
    user_id = ext.session_manager.get_current_user_id()
    posts   = ext.database_handler.get_posts()

    # Résolution des noms : { user_id: name }
    names = {
        post["user_id"]: ext.database_handler.get_name_from_id(post["user_id"])
        for post in posts
    }

    return render_template('chatroom/chatroom_home.html', id=user_id, posts=posts, names=names)


@bp.route('/create_post', methods=['GET', 'POST'])
@bp.route('/create_post/', methods=['GET', 'POST'])
@login_required
@require_permission("create_content")
def create_post():
    user_id = ext.session_manager.get_current_user_id()

    if request.method == 'GET':
        return render_template('chatroom/chatroom_create_post.html', id=user_id)

    title   = str(request.form['title'])
    content = str(request.form['content'])

    if not title or not content:
        flash('Error: Title and Content are required.')
        return redirect(url_for('chatroom.create_post'))

    ext.database_handler.create_post(user_id, title, content)
    return redirect(url_for('chatroom.chatroom'))


@bp.route('/edit_post/<int:id_post>', methods=['GET', 'POST'])
@bp.route('/edit_post/<int:id_post>/', methods=['GET', 'POST'])
@login_required
@require_permission("edit_own_content")
def edit_post(id_post: int):
    user_id = ext.session_manager.get_current_user_id()

    # Vérification de propriété
    if user_id != ext.database_handler.get_id_from_id_post(id_post):
        flash("You cannot edit this post.")
        return redirect(url_for('chatroom.chatroom'))

    if request.method == 'GET':
        post = ext.database_handler.get_post_from_id(id_post)
        return render_template('chatroom/chatroom_edit_post.html', id=user_id, post=post)

    title   = str(request.form['title'])
    content = str(request.form['content'])

    if not title or not content:
        flash('Error: Title and Content are required.')
        return redirect(url_for('chatroom.edit_post', id_post=id_post))

    ext.database_handler.update_post(id_post, title, content)
    return redirect(url_for('chatroom.chatroom'))


@bp.route('/delete/<int:id_post>', methods=['POST'])
@bp.route('/delete/<int:id_post>/', methods=['POST'])
@login_required
@require_permission("delete_own_content")
def delete_post(id_post: int):
    post = ext.database_handler.get_post_from_id(id_post)
    ext.database_handler.delete_post(id_post)
    flash(f'"{post["title"]}" was successfully deleted!')
    return redirect(url_for('chatroom.chatroom'))