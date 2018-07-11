from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import Post, Comment, Tag


def tags(count=10):
    fake=Faker()
    j = 0
    while j < count:
        t = Tag(name=fake.user_name())
        db.session.add(t)
        try: 
            db.session.commit()
            j += 1
        except:
            db.session.rollback()

def posts(count=100):
    fake = Faker()
    i=0
    tags_count = Tag.query.count()
    while i<count:
        b = fake.text()+fake.text()+fake.text()
        p = Post(body=b,
                 timestamp=fake.past_date(),
                 title=fake.text())
        t = Tag.query.offset(randint(0,tags_count-1)).first()
        p.tags.append(t)
        db.session.add(p)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()

def comments(count=100):
    fake = Faker()
    post_count = Post.query.count()
    for i in range(post_count):
        p = Post.query.offset(randint(0,post_count-1)).first()
        c = Comment(body=fake.text(),
                    author=fake.user_name(),
                    timestamp=fake.past_date(),
                    post=p)
        db.session.add(c)
    db.session.commit()


