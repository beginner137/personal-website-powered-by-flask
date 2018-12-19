from . import db, app
from .models import Post, Comment, Blog, Tag, Book
from flask import render_template, url_for, redirect, request,flash,session
from .decorators import admin_required
from .forms import CommentForm, LoginForm, PostForm, BookForm, NowForm

################### ERROR HANDLING ######################
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

################### NAVIGATION LINKS ######################
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/work')
def work():
    return render_template('work.html')

@app.route('/article')
def article():
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
    return render_template('article.html', posts=posts, pagination=pagination, tags=Tag.query)

@app.route('/book')
def book():
    query = Book.query
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Book.rec_level.desc()).paginate(
        page, per_page = app.config['POSTS_PER_PAGE'], error_out = False)
    books = pagination.items
    return render_template('book.html', books = books, pagination=pagination)

@app.route('/photo')
def photo():
    return render_template('photo.html')

@app.route('/now')
def now():
    query = Blog.query.filter_by(email="xiang_shenghua@hotmail.com").first()
    return render_template('now.html', content = query)


########################### LOGIN AND LOGOUT ##############################
@app.route('/alohomora', methods=['GET','POST'])
def alohomora():
    form = LoginForm()
    if form.validate_on_submit():
        blog= Blog.query.filter_by(email=form.email.data).first()
        if blog is not None and blog.verify(form.password.data):
            session['login'] = True
            return redirect(url_for('index'))
        flash('Invalid attempt!','error')
        return redirect(url_for('alohomora'))
    return render_template('alohomora.html', form=form)

@app.route('/colloportus')
@admin_required
def logout():
    session['login'] = False
    return redirect(url_for('index'))



######################## VIEW SINGLE POST ##################################
@app.route('/article/<int:id>', methods =['GET','POST'])
def single_article(id):
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
        return redirect(url_for('single_article',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.comments.count() -1) // app.config['COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page = app.config['COMMENTS_PER_PAGE'], error_out=False)
    comments= pagination.items
    return render_template('single_article.html', post = post,form=form, comments=comments,pagination=pagination,tags=Tag.query)

######################### VIEW SINGLE BOOK REVIEW #############################
@app.route('/book/<int:id>', methods =['GET','POST'])
def single_book(id):
    book = Book.query.get_or_404(id)
    return render_template('single_book.html', book = book)


########################### ADD A POST #####################################
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
        return redirect(url_for('article'))
    return render_template('add_post.html',form=form, tags=Tag.query)

########################### ADD A BOOK REVIEW #####################################
@app.route('/admin/add_book',methods=['GET','POST'])
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(book_name=form.name.data,
                    book_url = form.book_url.data,
                    book_image_link = form.book_image_link.data,
                    author=form.author.data,
                    rec_level = form.rec_level.data,
                    abstract=form.abstract.data,
                    body=form.body.data,
                    public=form.public.data)

        db.session.add(book)
        db.session.commit()
        flash('Your book review has been saved.')
        return redirect(url_for('book'))
    return render_template('add_book.html',form=form)


########################### EDIT A POST #####################################
@app.route('/admin/posts/<int:id>',methods=['GET','POST'])
@admin_required
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.abstract = form.abstract.data
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
        return redirect(url_for('single_article',id=post.id))
    form.title.data = post.title
    tags =''
    for tag in post.tags:
        if tags =='':
            tags = tag.name
        else:
            tags = tags+','+tag.name
    form.tags_hidden.data = tags
    form.abstract.data = post.abstract
    form.body.data = post.body
    form.public.data = post.public
    return render_template('edit_post.html', form=form,tags=Tag.query)


########################### EDIT A BOOK #####################################
@app.route('/admin/books/<int:id>',methods=['GET','POST'])
@admin_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm()
    if form.validate_on_submit():
        book = Book(book_name=form.name.data,
                    book_url = form.book_url.data,
                    book_image_link = form.book_image_link.data,
                    author=form.author.data,
                    rec_level = form.rec_level.data,
                    abstract=form.abstract.data,
                    body=form.body.data,
                    public=form.public.data)
        db.session.add(book)
        db.session.commit()
        flash('The book review has been updated')
        return redirect(url_for('single_book',id=book.id))
    form.name.data = book.book_name
    form.book_url.data = book.book_url
    form.book_image_link.data = book.book_image_link
    form.author.data = book.author
    form.rec_level.data = book.rec_level
    form.abstract.data = book.abstract
    form.body.data = book.body
    form.public.data = book.public
    return render_template('edit_book.html', form=form)

#####################EDIT NOW##########################
@app.route('/admin/now',methods=['GET','POST'])
@admin_required
def edit_now():
    info = Blog.query.filter_by(email="blog@example.com").first()
    form = NowForm()
    if form.validate_on_submit():
        info.now=form.body.data
        info.timestamp = form.timestamp.data
        db.session.commit()
        flash('Now content has been updated')
        return redirect(url_for('now'))
    form.body.data = info.now
    form.timestamp.data = info.timestamp
    return render_template('edit_now.html', form=form)



########################### DELETE A POST #####################################
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
    return redirect(url_for('article'))


########################### DELETE A BOOK #####################################
@app.route('/admin/delete_book/<int:id>', methods=['GET','POST','DELETE'])
@admin_required
def delete_book(id):
    Book.query.filter_by(id=id).delete()
    db.session.commit()
    flash('The book review has been deleted')
    return redirect(url_for('book'))

########################### SET A POST AS PRIVATE #####################################
@app.route('/admin/post/private/<int:id>')
@admin_required
def hide_post(id):
    post = Post.query.get(id)
    post.public = False
    db.session.add(post)
    db.session.commit()
    flash('The post has been set as private.')
    return redirect(url_for('article'))


########################### SET A BOOK AS PRIVATE #####################################
@app.route('/admin/book/private/<int:id>')
@admin_required
def hide_book(id):
    book = Book.query.get(id)
    book.public = False
    db.session.add(book)
    db.session.commit()
    flash('The book review has been set as private.')
    return redirect(url_for('book'))

########################### SET A POST AS PUBLIC #####################################
@app.route('/admin/post/public/<int:id>')
@admin_required
def show_post(id):
    post = Post.query.get(id)
    post.public = True
    db.session.add(post)
    db.session.commit()
    flash('The post has been set as public.')
    return redirect(url_for('article'))


########################### SET A BOOK AS PUBLIC #####################################
@app.route('/admin/book/public/<int:id>')
@admin_required
def show_book(id):
    book = Book.query.get(id)
    book.public = True
    db.session.add(book)
    db.session.commit()
    flash('The book review has been set as public.')
    return redirect(url_for('book'))

########################### MODERATE COMMENTS #####################################
@app.route('/admin/comments')
@admin_required
def moderate_comments():
    page = request.args.get('page',1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=app.config['COMMENTS_PER_PAGE'],error_out=False)
    comments = pagination.items
    return render_template('moderate_comments.html',comments=comments,pagination=pagination, page=page,tags=Tag.query)

########################### ENABLE A COMMENT #####################################
@app.route('/admin/comments/enable/<int:id>')
@admin_required
def comment_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash('This comment has been enabled.')
    return redirect(url_for('moderate_comments', page=request.args.get('page',1,type=int)))

########################### DISABLE A COMMENT ###################
@app.route('/admin/comments/disable/<int:id>')
@admin_required
def comment_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash('This comment has been disabled')
    return redirect(url_for('moderate_comments', page=request.args.get('page',1,type=int)))

#####################DELETE A COMMENT##############################
@app.route('/admin/delete_comment/<int:id>')
@admin_required
def delete_comment(id):
    Comment.query.filter_by(id=id).delete()
    db.session.commit()
    flash('The comment has been deleted')
    return redirect(url_for('moderate_comments',page=request.args.get('page',1,type=int)))

########################VIEW POSTS BY TAG#########################
@app.route('/tags/<name>')
def tag_posts(name):
    tag = Tag.query.filter_by(name=name).first()
    query= tag.posts
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('tag_posts.html',posts=posts,pagination=pagination,tag=name,tags=Tag.query)

