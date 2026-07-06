from flask import Blueprint, request
from src.models import Usuario, db
from src.app import bcrypt
from http import HTTPStatus
from flask_jwt_extended import create_access_token



app = Blueprint('auth', __name__, url_prefix="/auth")

def _valid_password(password_hash, password_raw):
    return bcrypt.check_password_hash(password_hash, password_raw)

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    # O jeito correto: Classe.coluna == variavel_string
    usuario = db.session.execute(db.select(Usuario).where(Usuario.username == username)).scalar()

    if not usuario or not _valid_password (usuario.password, password):        
        return {"msg": "Usuário ou senha inválidos"}, HTTPStatus.UNAUTHORIZED

    access_token = create_access_token(identity=str(usuario.id))
    return {"access_token":access_token}
