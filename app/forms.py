from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,SubmitField, PasswordField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Length,Email
from flask_pagedown.fields import PageDownField

class CommentForm(FlaskForm):
    body = TextAreaField('Comment',validators=[DataRequired(), Length(1,300)])
    author = StringField('Name',validators=[DataRequired(),Length(1,16)])
    email = StringField('Email Address',validators=[DataRequired(),Email()])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    abstract = PageDownField('Abstract', validators=[DataRequired()])
    body = PageDownField("Add a post", validators=[DataRequired()])
    tag = StringField('Tag(s)')
    tags_hidden = TextAreaField('')
    public = BooleanField("Make public")
    submit = SubmitField('Save')

class BookForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    book_url = StringField('Enter book url, goodreads or amazon',validators=[DataRequired()])
    book_image_link = StringField('Enter book image url')
    author = StringField('Book author',validators=[DataRequired()])
    rec_level = IntegerField('Recommendation level', validators=[DataRequired()])
    abstract = PageDownField('Abstract',validators=[DataRequired()])
    body = PageDownField('Add a book review',validators=[DataRequired()])
    public = BooleanField("Make public")
    submit = SubmitField('Save')

class NowForm(FlaskForm):
    body = PageDownField("What I'm doing now", validators=[DataRequired()])
    timestamp = StringField("Today's date", validators=[DataRequired()])
    submit = SubmitField('Save')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64),Email()])
    password = PasswordField('Magic words', validators=[DataRequired()])
    submit = SubmitField('Submit')