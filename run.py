import os 
from flask_migrate import upgrade
from app import app,db
from app.models import Post,Comment,Blog,Tag


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Post=Post, Comment=Comment,Blog=Blog,Tag=Tag)

@app.cli.command()
def deploy():
    upgrade()

    Blog.add_admin()

if __name__=='__main__':
    app.run(debug=True)

