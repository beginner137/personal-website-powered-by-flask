from functools import wraps
from flask import abort, session, redirect, url_for

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('login'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function