from posts_app.config.mysqlconnection import connectToMySQL, db
from posts_app import app
from posts_app.models import post, like
from flask import flash, session
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re

# ==================
# PATTERN VALIDATORS
# ==================
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$')
PWD_REGEX = re.compile(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*?])[\w\d!@#$%^&*?]{6,12}$")


# ===================
# INITIALIZE INSTANCE
# ===================
class User:
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.posts = []
        self.likes = []

    # INSTANCE METHODS
    def return_full_name(self):
        return f'{self.first_name} {self.last_name}'



    # =============
    # CLASS METHODS
    # =============

    # ===========
    #  CREATE SQL
    # ===========
    @classmethod
    def create_user(cls,form_data):
        if not cls.vaildate_user_form(form_data):
            return False
        data = cls.parse_user_form_data(form_data)
        query = '''
        INSERT INTO users 
        (first_name,last_name,email,password)
        VALUES
        (%(first_name)s,%(last_name)s,%(email)s,%(password)s);
        '''
        user_id = connectToMySQL(db).query_db(query,data)
        session['user_id'] = user_id
        session['email'] = data['email']
        session['user_name'] = f'{data["first_name"]} {data["last_name"]}'
        return True



    # ========
    # READ SQL
    # ========
    @classmethod
    def get_all_users(cls):
        query = '''
        SELECT * FROM users;
        '''
        results = connectToMySQL(db).query_db(query)
        all_users = []
        if results:
            for person in results:
                this_user = {
                    'id': person['id'],
                    'first_name': person['first_name'],
                    'last_name': person['last_name'],
                    'email': person['email'],
                    'password': person['password'],
                    'created_at': person['created_at'],
                    'updated_at': person['updated_at']
                }
                all_users.append(cls(this_user))
            return all_users
        return False

    @classmethod
    def get_user_by_id(cls,id):
        data = {'id':id}
        query = '''
        SELECT users.id, first_name, last_name,
        email,password,users.created_at,users.updated_at,
        posts.id,content,posts.created_at,posts.updated_at,
        posts.user_id,likes.post_id
        FROM users
        JOIN posts
        ON posts.user_id = users.id
        LEFT JOIN likes
        ON likes.post_id = posts.id
        WHERE users.id = %(id)s
        GROUP BY posts.id;
        '''
        results = connectToMySQL(db).query_db(query,data)
        if results:
            this_user = cls(results[0])
            for each_row in results:
                post_data = {
                    'id': each_row['posts.id'],
                    'user_id': each_row['user_id'],
                    'content': each_row['content'],
                    'created_at': each_row['posts.created_at'],
                    'updated_at': each_row['posts.updated_at'],
                }
                like_data = {
                    'user_id': each_row['user_id'],
                    'post_id': each_row['post_id']
                }
                this_user.likes.append(like.Like(like_data))
                this_user.posts.append(post.Post(post_data))
            return this_user
        return False

    @classmethod
    def get_user_be_email(cls, email):
        data = {'email':email}
        query = '''
        SELECT *
        FROM users
        WHERE email = %(email)s;
        '''
        result = connectToMySQL(db).query_db(query,data)
        if result:
            result = cls(result[0])
            return result
        return False



    # ==========
    # UPDATE SQL
    # ==========
    @classmethod
    def update_user(cls,form_data):
        data = cls.parse_user_form_data(form_data)
        data['id'] = session['user_id']
        if not cls.vaildate_user_form(data):
            return False
        query = '''
        UPDATE users
        SET 
        first_name = %(first_name)s,
        last_name = %(last_name)s,
        email = %(email)s
        WHERE id = %(id)s;
        '''
        connectToMySQL(db).query_db(query,data)
        return True



    # ==========
    # DELETE SQL
    # ==========
    @classmethod
    def delete_user(cls,id):
        data = {'id':id}
        query = '''
        DELETE FROM users
        WHERE id = %(id)s;
        '''
        return connectToMySQL(db).query_db(query,data)


    # ==============
    # STATIC METHODS
    # ==============

    @staticmethod
    def vaildate_user_form(form_data):
        is_valid = True
        if 'id' in form_data:
            if User.get_user_be_email(form_data['email']) and form_data['email'] != session['email']:
                flash('Sorry this email is already in use..')
                is_valid = False
        else:
            if User.get_user_be_email(form_data['email']):
                flash('Sorry this email is already in use..')
                is_valid = False
        if len(form_data['first_name']) < 2:
            flash('First name must be 2 or characters')
            is_valid = False
        if len(form_data['last_name']) < 2:
            flash('Last name must be 2 or characters')
            is_valid = False
        if not EMAIL_REGEX.match(form_data['email']):
            flash('Please enter a valid email...')
            is_valid = False
        if 'password' in form_data:
            if not PWD_REGEX.match(form_data['password']):
                flash('''Password must have capitol/lowercase letters,
                        a number, and a specail charater''')
                is_valid = False
            if form_data['password'] != form_data['confirm_password']:
                flash('Passwords do not match...')
                is_valid = False
        return is_valid

    @staticmethod
    def login_user(data):
        this_user = User.get_user_be_email(data['email'].lower())
        if this_user:
            if bcrypt.check_password_hash(this_user.password, data['password']):
                session['user_id'] = this_user.id
                session['email'] = this_user.email
                session['user_name'] = f'{this_user.first_name} {this_user.last_name}'
                return True
        flash('Invalid email/password')
        return False

    @staticmethod
    def parse_user_form_data(form_data):
        parsed_data = {}
        parsed_data['first_name'] = form_data['first_name'].strip()
        parsed_data['last_name'] = form_data['last_name'].strip()
        parsed_data['email'] = form_data['email'].lower().strip()
        if 'password' in form_data:
            parsed_data['password'] = bcrypt.generate_password_hash(form_data['password'])
        return parsed_data



# SELECT users.id fist_name, last_name,
# email,password,users.created_at,users.updated_at,
# posts.id,content,posts.created_at,posts.updated_at,
# posts.user_id,likes.post_id
# FROM posts
# LEFT JOIN users
# ON posts.user_id = users.id
# LEFT JOIN likes
# ON likes.post_id = posts.id
# WHERE users.id = 1
# GROUP BY posts.id;