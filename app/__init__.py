import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_pagedown import PageDown
from werkzeug.contrib.fixers import ProxyFix
from flask_migrate import Migrate, upgrade


app = Flask(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'whatever'
PASSWD = os.environ.get('BLOG_PASSWD')
POSTS_PER_PAGE = 5
COMMENTS_PER_PAGE = 5
BLOG_ADMIN = 'blog@example.com' or os.environ.get('BLOG_ADMIN')
SSL_REDIRECT = True if os.environ.get('DYNO') else False

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(app.root_path,'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(__name__)

if app.config['SSL_REDIRECT']:
    from flask_sslify import SSLify
    sslify = SSLify(app)


app.wsgi_app = ProxyFix(app.wsgi_app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
pagedown = PageDown(app)
migrate = Migrate(app,db)


from app import views
from app.models import Post,Comment,Blog,Tag,Book

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Post=Post, Comment=Comment,Blog=Blog,Tag=Tag,Book=Book)

@app.cli.command()
def deploy():
    Blog.add_admin()