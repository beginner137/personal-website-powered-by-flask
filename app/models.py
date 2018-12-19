from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from app import db, app
from datetime import datetime
import bleach
from markdown import markdown


default_passwd = ''

registrations = db.Table('registrations',
        db.Column('post_id',db.Integer,db.ForeignKey('posts.id')),
        db.Column('tag_id',db.Integer, db.ForeignKey('tags.id'))
    )

allowed_attrs = ['img','src','alt','width','height','br']

allowed_tags = ['a','abbr', 'acronym', 'b','blockquote','code',
                'em','i','li','ol','pre','strong','ul',
                'h1','h2','h3','p','img','br','iframe']

class Blog(db.Model):
    __tablename__ = 'info'     

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    running_since = db.Column(db.DateTime(), default=datetime.utcnow)
    timestamp = db.Column(db.String(32))
    now = db.Column(db.Text)
    now_html = db.Column(db.Text)
    
    @staticmethod
    def on_changed_now(target, value, oldvalue, initiator):
        target.now_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),tags=allowed_tags))

    @staticmethod
    def add_admin():
        blog = Blog(email=app.config['BLOG_ADMIN'],password_hash=default_passwd)
        db.session.add(blog)
        db.session.commit()

    def verify(self, password):
        return check_password_hash(self.password_hash, password)
    
    def change_password(self, old_password, new_password):
        if not self.check_password_hash(self.password_hash, old_password):
            flash('Wrong password!')
            return False
        self.password_hash = generate_password_hash(new_password)
        flash('Password updated!')
        return True

db.event.listen(Blog.now,'set',Blog.on_changed_now)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    abstract = db.Column(db.Text)
    abstract_html = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    public = db.Column(db.Boolean, default=False, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', 
                            secondary=registrations,
                            backref=db.backref('posts',lazy='dynamic'))

    @staticmethod
    def on_changed_abstract(target,value,oldvalue, initiator):

        target.abstract_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'), tags=allowed_tags, attributes=allowed_attrs,strip=False))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),tags=allowed_tags,attributes=allowed_attrs, strip=False))

db.event.listen(Post.abstract,'set',Post.on_changed_abstract)
db.event.listen(Post.body,'set',Post.on_changed_body)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author = db.Column(db.String(140))
    email = db.Column(db.String(64), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),strip=True))
db.event.listen(Comment.body,'set',Post.on_changed_body)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key = True)
    book_url = db.Column(db.String(140))
    book_image_link = db.Column(db.String(256))
    book_name = db.Column(db.Text)
    author = db.Column(db.String(32))
    rec_level = db.Column(db.Float)
    abstract = db.Column(db.Text)
    abstract_html = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    public = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def on_changed_abstract(target,value,oldvalue, initiator):
        target.abstract_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),tags=allowed_tags,attributes=allowed_attrs))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),tags=allowed_tags,attributes=allowed_attrs))

db.event.listen(Book.abstract,'set',Post.on_changed_abstract)
db.event.listen(Book.body,'set',Post.on_changed_body)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64), unique=True)


