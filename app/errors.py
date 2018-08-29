from app import app
from flask import render_template
from models import Tag

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