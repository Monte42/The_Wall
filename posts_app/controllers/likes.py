from posts_app import app
from flask import redirect
from posts_app.models import like




# ===================
# CREATE/DELETE ROUTE
# ===================
@app.route('/like/<int:id>')
def like_post(id):
    if like.Like.user_has_not_liked_this(id):like.Like.create_like(id)
    return redirect(f'/wall#{id}')