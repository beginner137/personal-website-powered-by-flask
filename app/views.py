from . import db, app
from .models import Post, Comment, Blog, Tag
from flask import render_template, url_for, redirect, request,flash,session
from .decorators import admin_required
from .forms import CommentForm, LoginForm, PostForm


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html', tags=Tag.query),403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html',tags=Tag.query),404

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html',tags=Tag.query),400

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html',tags=Tag.query),500

@app.route('/')
def index():
    query = Post.query.filter_by(public=True)
    try:
        if session['login']:
            query = Post.query
    except:
        query = query 

    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    #return render_template('index.html',info = blog_info(), posts=posts, pagination=pagination)
    return render_template('index.html',posts=posts, pagination=pagination, single_post=False, tags=Tag.query)

@app.route('/about_me')
def about_me():
    return render_template('about_me.html',tags=Tag.query)

@app.route('/about_this_blog')
def about_blog():
    return render_template('about_this_blog.html',tags=Tag.query)

@app.route('/post/<int:id>', methods =['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form  = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=form.author.data,
                          email=form.email.data)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published')
        return redirect(url_for('post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.comments.count() -1) // app.config['COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page = app.config['COMMENTS_PER_PAGE'], error_out=False)
    comments= pagination.items
    return render_template('post.html', posts=[post], single_post=True,form=form, comments=comments,pagination=pagination,tags=Tag.query)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        blog= Blog.query.filter_by(email=form.email.data).first()
        if blog is not None and blog.verify(form.password.data):
            session['login'] = True
            return redirect(url_for('admin'))
        flash('Invalid attempt!')
        return redirect(url_for('login'))
    return render_template('login.html', form=form,tags=Tag.query)


@app.route('/admin/')
@admin_required
def admin():
    query = Post.query
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('admin.html',posts=posts, pagination=pagination, single_post=False, tags=Tag.query)

@app.route('/admin/add_post',methods=['GET','POST'])
@admin_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    public=form.public.data)
        tags = form.tags_hidden.data
        tags_split = tags.split(',')
        for tag in tags_split:
            t = Tag.query.filter_by(name=tag).first()
            if t is not None:
                post.tags.append(t)
            else:
                new_tag = Tag(name=tag)
                post.tags.append(new_tag)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been saved.')
        return redirect(url_for('admin'))
    return render_template('add_post.html',form=form, tags=Tag.query)

@app.route('/admin/posts/<int:id>',methods=['GET','POST'])
@admin_required
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        if form.public.data:
            post.public = True
        else:
            post.public= False
        tags = form.tags_hidden.data
        tags_split = tags.split(',')
        for tag in tags_split:
            t = Tag.query.filter_by(name=tag).first()
            if t is not None:
                if t not in post.tags:
                    post.tags.append(t)
            else:
                new_tag = Tag(name=tag)
                post.tags.append(new_tag)
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated')
        return redirect(url_for('post',id=post.id))
    form.title.data = post.title
    tags =''
    for tag in post.tags:
        if tags =='':
            tags = tag.name
        else:
            tags = tags+','+tag.name
    form.tags_hidden.data = tags
    form.body.data = post.body
    return render_template('edit_post.html', form=form,tags=Tag.query)

@app.route('/admin/delete_post/<int:id>', methods=['GET','POST','DELETE'])
@admin_required
def delete_post(id):
    p = Post.query.filter_by(id=id).first()
    p.tags.clear()
    Post.query.filter_by(id=id).delete()
    tags = Tag.query
    for tag in tags:
        if int(tag.posts.count()) == 0:
            Tag.query.filter_by(id=tag.id).delete()
            db.session.commit()
    db.session.commit()
    flash('The post has been deleted')
    return redirect(url_for('index'))

@app.route('/admin/post/private/<int:id>')
@admin_required
def hide_post(id):
    post = Post.query.get(id)
    post.public = False
    db.session.add(post)
    db.session.commit()
    flash('The post has been set as private.')
    return redirect(url_for('index'))

@app.route('/admin/post/public/<int:id>')
@admin_required
def show_post(id):
    post = Post.query.get(id)
    post.public = True
    db.session.add(post)
    db.session.commit()
    flash('The post has been set as public.')
    return redirect(url_for('index'))

@app.route('/admin/comments')
@admin_required
def moderate_comments():
    page = request.args.get('page',1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=app.config['COMMENTS_PER_PAGE'],error_out=False)
    comments = pagination.items
    return render_template('moderate_comments.html',comments=comments,pagination=pagination, page=page,tags=Tag.query)


@app.route('/admin/comments/enable/<int:id>')
@admin_required
def comment_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash('This comment has been enabled.')
    return redirect(url_for('moderate_comments', page=request.args.get('page',1,type=int)))

@app.route('/admin/comments/disable/<int:id>')
@admin_required
def comment_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash('This comment has been disabled')
    return redirect(url_for('moderate_comments', page=request.args.get('page',1,type=int)))

@app.route('/admin/delete_comment/<int:id>')
@admin_required
def delete_comment(id):
    Comment.query.filter_by(id=id).delete()
    db.session.commit()
    flash('The comment has been deleted')
    return redirect(url_for('moderate_comments',page=request.args.get('page',1,type=int)))


@app.route('/tags/<name>')
def tag_posts(name):
    tag = Tag.query.filter_by(name=name).first()
    query= tag.posts
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('tag_posts.html',posts=posts,pagination=pagination,tag=name,tags=Tag.query)

@app.route('/logout')
@admin_required
def logout():
    session['login'] = False
    return redirect(url_for('index'))