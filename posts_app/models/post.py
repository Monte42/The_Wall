from flask import flash,session
from posts_app.config.mysqlconnection import connectToMySQL, db
from posts_app.models import user, like


# ===================
# INITIALIZE INSTANCE
# ===================
class Post:
    def __init__(self,data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user = None
        self.likes = []

    # INSTANCE METHODS
    def return_like_count(self):
        if type(self.likes) == list:return len(self.likes)
        return self.likes



    # =============
    # CLASS METHODS
    # =============

    # ===========
    #  CREATE SQL
    # ===========
    @classmethod
    def create_post(cls,form_data):
        if not cls.validate_post_from(form_data):return False
        data = form_data.copy()
        data['user_id'] = session['user_id']
        query = '''
        INSERT INTO posts
        (user_id, content)
        VALUES
        (%(user_id)s,%(content)s);
        '''
        return connectToMySQL(db).query_db(query, data)



    # ========
    # READ SQL
    # ========
    @classmethod
    def get_all_posts(cls):
        query = '''
        SELECT *, 
        COUNT(likes.post_id) 
        AS like_count
        FROM posts
        JOIN users
        ON posts.user_id = users.id
        LEFT JOIN likes
        ON likes.post_id = posts.id
        GROUP BY posts.id
        ORDER BY posts.created_at
        DESC;
        '''
        all_posts = []
        results = connectToMySQL(db).query_db(query)
        if results:
            for each_post in results:
                this_post = cls(each_post)
                user_data = {
                    'id': each_post['users.id'],
                    'first_name': each_post['first_name'],
                    'last_name': each_post['last_name'],
                    'email': each_post['email'],
                    'password': each_post['password'],
                    'created_at': each_post['users.created_at'],
                    'updated_at': each_post['users.updated_at']
                }
                this_post.user = user.User(user_data)
                this_post.likes = each_post['like_count']
                all_posts.append(this_post)
        return all_posts

    @classmethod
    def get_post_by_id(cls, id):
        data = {'id':id}
        query = '''
        SELECT * FROM posts
        JOIN users
        ON users.id = posts.user_id
        LEFT JOIN likes
        ON posts.id = likes.post_id
        LEFT JOIN users AS users2
        ON users2.id = likes.user_id
        WHERE posts.id = %(id)s;
        '''
        results = connectToMySQL(db).query_db(query,data)
        if results:
            this_post = cls(results[0])
            user_data = {
                    'id': results[0]['users.id'],
                    'first_name': results[0]['first_name'],
                    'last_name': results[0]['last_name'],
                    'email': results[0]['email'],
                    'password': results[0]['password'],
                    'created_at': results[0]['users.created_at'],
                    'updated_at': results[0]['users.updated_at']
                }
            this_post.user = user.User(user_data)
            for row in results:
                user_data = {
                    'id': row['users2.id'],
                    'first_name': row['users2.first_name'],
                    'last_name': row['users2.last_name'],
                    'email': row['users2.email'],
                    'password': row['users2.password'],
                    'created_at': row['users2.created_at'],
                    'updated_at': row['users2.updated_at']
                }
                like_data = {
                    'user_id': row['likes.user_id'],
                    'post_id': row['id'],
                }
                this_like = like.Like(like_data)
                this_like.user = user.User(user_data)
                this_like.post = this_like
                this_post.likes.append(this_like)
            return this_post
        return False




    # ==========
    # UPDATE SQL
    # ==========
    @classmethod
    def update_post(cls,form_data,id):
        if not cls.validate_post_from(form_data): return False
        data = form_data.copy()
        data['id'] = id
        data['user_id'] = session['user_id']
        query = '''
        UPDATE posts
        SET
        content = %(content)s
        WHERE id = %(id)s;
        '''
        return connectToMySQL(db).query_db(query,data)



    # ==========
    # DELETE SQL
    # ==========
    @classmethod
    def delete_post(cls, id):
        data = {'id':id}
        query= '''
        DELETE FROM posts
        WHERE id = %(id)s;
        '''
        return connectToMySQL(db).query_db(query,data)



    # ==============
    # STATIC METHODS
    # ==============

    # FORM VALIDATIONS
    @staticmethod
    def validate_post_from(form_data):
        is_valid = True
        if len(form_data['content']) < 1:
            flash('Post can not be empty')
            is_valid = False
        return is_valid