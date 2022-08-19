from posts_app import app
from flask import render_template, redirect, request,flash, session
from posts_app.models import post



# =============
#  CREATE ROUTE
# =============
@app.route('/create_post', methods=['POST'])
def create_post():
    if not session.get('user_id'): return redirect('/')
    post.Post.create_post(request.form)
    return redirect('/wall')



# ===========
# READ ROUTE
# ===========
@app.route('/wall')
def the_wall():
    if not session.get('user_id'): return redirect('/')
    all_posts = post.Post.get_all_posts()
    return render_template('posts/wall.html', posts=all_posts)

@app.route('/post/<int:id>')
def one_post(id):
    if not session.get('user_id'): return redirect('/')
    this_post = post.Post.get_post_by_id(id)
    return render_template('posts/post.html', post=this_post)



# ============
# UPDATE ROUTE
# ============
@app.route('/post/<int:id>/edit', methods=['POST','GET'])
def edit_post(id):
    if not session.get('user_id'): return redirect('/')
    if request.method != "POST":
        flash('You can not edit posts this way...')
        return redirect('/wall')
    this_post = post.Post.get_post_by_id(id)
    if session['user_id'] != this_post.user_id:
        flash('You are not authorized to do that!')
        return redirect('/wall')
    post.Post.update_post(request.form,id)
    return redirect(f'/wall#{id}')



# ============
# DELETE ROUTE
# ============
@app.route('/post/<int:id>/delete')
def delete_post(id):
    if not session.get('user_id'): return redirect('/')
    if not post.Post.get_post_by_id(id):
        flash('You can not delete posts this way...')
        return redirect('/wall')
    this_post = post.Post.get_post_by_id(id)
    if session['user_id'] != this_post.user_id:
        flash("You are not authorized to do that!")
        return redirect('/wall')
    post.Post.delete_post(id)
    return redirect('/wall')