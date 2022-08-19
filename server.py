from posts_app import app
from posts_app.controllers import users, posts, likes

if __name__ == "__main__":
    app.run(debug=True)