from flask import session, request, redirect, url_for
from functools import wraps

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ✅ For global login enforcement
def require_login_globally():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('login'))