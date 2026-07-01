from flask import Blueprint, request
from src.app import Usuario, db
from http import HTTPStatus
from flask_jwt_extended import create_access_token


app = Blueprint('auth', __name__, url_prefix="/auth")

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    # O jeito correto: Classe.coluna == variavel_string
    usuario = db.session.execute(db.select(Usuario).where(Usuario.username == username)).scalar()

    if not usuario or usuario.password != password:
        return {"msg": "Usuário ou senha inválidos"}, HTTPStatus.UNAUTHORIZED

    access_token = create_access_token(identity=str(usuario.id))
    return {"access_token":access_token}
