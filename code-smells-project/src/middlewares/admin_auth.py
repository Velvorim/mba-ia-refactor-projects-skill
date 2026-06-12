import os
from functools import wraps
from flask import request, jsonify

# PT-09: Middleware de autenticacao para endpoints admin
def require_admin_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        admin_token = os.environ.get("ADMIN_TOKEN", "")
        if not admin_token or not token or token != admin_token:
            return jsonify({"erro": "Nao autorizado", "sucesso": False}), 401
        return f(*args, **kwargs)
    return decorated
