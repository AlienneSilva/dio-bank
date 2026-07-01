from flask_jwt_extended import get_jwt_identity
from src.app import Usuario, db
from http import HTTPStatus
from functools import wraps


def required_role(role_name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
        # 1. O JWT recupera a identidade como string (ex: "1")
            usuario_id = get_jwt_identity()       
         
        # 3. Agora o banco busca por número perfeitamente
            usuario = db.get_or_404(Usuario, usuario_id)

            if usuario.role.name != role_name :
                return {"message": "User don't have access."}, HTTPStatus.FORBIDDEN
            return f(*args, **kwargs)
        return wrapped
    return decorator

def eleva_quadrado(x):
    return x**2