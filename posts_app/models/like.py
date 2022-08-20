from posts_app.config.mysqlconnection import connectToMySQL, db
from posts_app. models import user, post
from flask import session


# ===================
# INITIALIZE INSTANCE
# ===================
class Like:
    def __init__(self,data):
        self.user_id = data['user_id']
        self.post_id = data['post_id']
        self.user = None
        self.post = None



    # =============
    # CLASS METHODS
    # =============

    # ===========
    #  CREATE SQL
    # ===========
    @classmethod
    def create_like(cls,post_id):
        data = {
            'post_id': post_id,
            'user_id': session['user_id']
            }
        query = '''
        INSERT INTO likes
        (user_id, post_id)
        VALUES
        (%(user_id)s,%(post_id)s);
        '''
        return connectToMySQL(db).query_db(query, data)



    # ========
    # READ SQL
    # ========
    @classmethod
    def get_likes_by_post(cls,post_id):
        data = {'post_id': post_id,}
        query = '''
        SELECT * from posts
        JOIN likes
        ON likes.post_id = posts.id
        JOIN users
        ON likes.user_id = users.id
        WHERE posts.id = %(post_id)s;
        '''
        results = connectToMySQL(db).query_db(query, data)
        all_post_likes = []
        if results:
            this_like = cls(results[0])
            for post_like in results:
                post_data = {
                    'id': post_like['id'],
                    'user_id': post_like['user_id'],
                    'content': post_like['content'],
                    'created_at': post_like['created_at'],
                    'updated_at': post_like['updated_at'],
                }
                user_data = {
                    'id': post_like['users.id'],
                    'first_name': post_like['first_name'],
                    'last_name': post_like['last_name'],
                    'email': post_like['email'],
                    'password': post_like['password'],
                    'created_at': post_like['users.created_at'],
                    'updated_at': post_like['users.updated_at']
                }
                this_like.user = user.User(user_data)
                this_like.post = post.Post(post_data)
                all_post_likes.append(this_like)
        return all_post_likes



    # ==========
    # DELETE SQL
    # ==========
    @classmethod
    def delete_like(cls,user_id, post_id):
        data = {
            'user_id':user_id,
            'post_id':post_id
        }
        query = '''
        DELETE FROM likes
        WHERE user_id = %(user_id)s
        AND post_id = %(post_id)s;
        '''
        return connectToMySQL(db).query_db(query,data)



    # ==============
    # STATIC METHODS
    # ==============
    @staticmethod
    def user_has_not_liked_this(id):
        this_post_likes_list = Like.get_likes_by_post(id)
        for like in this_post_likes_list:
            if like.user.id == session['user_id']:
                Like.delete_like(session['user_id'], id)
                return False
        return True