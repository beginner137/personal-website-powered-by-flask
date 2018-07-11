from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired,Length,Email
from flask_pagedown.fields import PageDownField

class CommentForm(FlaskForm):
    body = TextAreaField('Comment',validators=[DataRequired(), Length(1,300)])
    author = StringField('Name',validators=[DataRequired(),Length(1,16)])
    email = StringField('Email Address',validators=[DataRequired(),Email()])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = PageDownField("Add a post", validators=[DataRequired()])
    tag = StringField('Tag(s)')
    tags_hidden = TextAreaField('')
    public = BooleanField("Make public")
    submit = SubmitField('Save')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64),Email()])
    password = PasswordField('Magic words that can manage the blog', validators=[DataRequired()])
    submit = SubmitField('Submit')