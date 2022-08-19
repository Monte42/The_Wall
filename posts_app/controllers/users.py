from posts_app import app
from flask import render_template, redirect, request,flash, session
from posts_app.models import user


# ====================
# REGISTER/LOGIN ROUTE
# ====================
@app.route('/')
def login_register_page():
    if session.get('user_id'): return redirect('/wall')
    return render_template('index.html',data=None,login_data=None)

# =================
# CREATE USER ROUTE
# =================
@app.route('/register', methods=['POST'])
def register_user():
    if user.User.create_user(request.form):return redirect('/wall')
    return render_template('index.html',data=request.form,login_data=None)

# ===============
# LOGIN USER POST
# ===============
@app.route('/login', methods=["POST"])
def login():
    if user.User.login_user(request.form):return redirect('/wall')
    return render_template('index.html',data=None,login_data=request.form)

# =================
# LOGOUT USER ROUTE
# =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



# ===========
# READ ROUTES
# ===========
# GET ALL USER
@app.route('/users')
def get_all_users():
    if not session.get('user_id'):return redirect('/')
    all_users = user.User.get_all_users()
    return render_template('users/all_users.html', users=all_users)
    

# GET SINGLE USER
@app.route('/users/<int:id>')
def get_single_user(id):
    if not session.get('user_id'):return redirect('/')
    this_user = user.User.get_user_by_id(id)
    if this_user:
        return render_template('users/user_profile.html', user=this_user)
    



# =================
# UPDATE USER ROUTE
# =================
@app.route('/users/<int:id>/edit', methods = ["GET","POST"])
def update_user(id):
    if not session.get('user_id'):return redirect('/')
    if request.method == 'GET':
        if not user.User.get_user_by_id(id):
            flash('This user does not exist...')
            return redirect('/users')
        this_user = user.User.get_user_by_id(id)
        if this_user.id == session['user_id']:return render_template('users/update_user.html', data=this_user)
        flash('You are not authorized to do that!')
        return redirect('/users')
    if user.User.update_user(request.form):return redirect(f'/users/{id}')
    return redirect(f'/users/{id}/edit')
    



# =================
# DELETE USER ROUTE
# =================
@app.route('/users/<int:id>/delete')
def delete_user(id):
    if session.get('user_id'):
        if not user.User.get_user_by_id(id):
            flash('This user does not exist...')
            return redirect('/users')
        if session['user_id'] != id:
            flash("You are not authorized to do that!")
            return redirect('/users')
        user.User.delete_user(id)
        session.clear()
    return redirect('/')