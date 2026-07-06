from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy import inspect
from src.app import bcrypt
from src.models import Usuario, db
from src.utils import required_role
from src.views.user import  CreateUserSchema, UsuarioSchema




app = Blueprint('usuario', __name__, url_prefix="/usuarios")



def _create_usuario():
    user_schema = CreateUserSchema()
    try:
        data = user_schema.load(request.json)  
    except ValidationError as exc:
        return exc.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    # Criamos APENAS UM usuário com todos os dados juntos
    novo_usuario = Usuario(
        username=data["username"],
        password=bcrypt.generate_password_hash(data["password"]).decode('utf-8'),
        role_id=data["role_id"],
    )
    
    # Adicionamos esse único usuário na sessão
    db.session.add(novo_usuario)
    db.session.commit()
    return {"message": "Usuario criado!"}, HTTPStatus.CREATED

@jwt_required()
@required_role("Admin")
def _list_usuarios():
    query = db.select(Usuario)
    usuarios = db.session.execute(query).scalars()
    usuarios_schema = UsuarioSchema(many=True)
    return usuarios_schema.dump(usuarios)
    



@app.route('/', methods=['GET', 'POST'])
def handle_usuario():
    if request.method == 'POST':
        return _create_usuario()        
    else:
        return {"Usuarios": _list_usuarios()}
    

@app.route('/<int:usuario_id>')
def get_usuario(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    return {"id": usuario.id,"username": usuario.username}

@app.route('/<int:usuario_id>', methods=["PATCH"])  # PUT = atualiza todos os campos // PATH = atualiza somente o campo solitado 
def update_usuario(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    data = request.json   

    mapper =  inspect(Usuario)
    for column in mapper.attrs:
        if column.key in data:
            setattr(usuario, column.key, data[column.key])
    db.session.commit()


    return {        
        "id": usuario.id, "username": usuario.username
    }

@app.route('/<int:usuario_id>', methods=["DELETE"])
def delete_usuario(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    db.session.delete(usuario)
    db.session.commit()

    return "", HTTPStatus.NO_CONTENT