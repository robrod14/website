# routes/utils/auth.py
from functools import wraps
from flask import request, jsonify, session

# existing ADMIN_TOKEN + require_admin stays above...

def require_admin_session(f):
    """Protect routes using session-based admin login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
