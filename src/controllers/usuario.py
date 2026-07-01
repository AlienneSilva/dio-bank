from flask import Blueprint, request
from src.app import Usuario, db
from http import HTTPStatus
from sqlalchemy import inspect
from flask_jwt_extended import jwt_required
from src.utils import required_role

app = Blueprint('usuario', __name__, url_prefix="/usuarios")



def _create_usuario():
    data = request.json    
    # Criamos APENAS UM usuário com todos os dados juntos
    novo_usuario = Usuario(
        username=data["username"],
        password=data["password"],
        role_id=data["role_id"],
    )
    
    # Adicionamos esse único usuário na sessão
    db.session.add(novo_usuario)
    db.session.commit()

def _list_usuarios():
    query = db.select(Usuario)
    results = db.session.execute(query).scalars().all()
    return results



@app.route('/', methods=['GET', 'POST'])
@jwt_required()
@required_role("Admin")
def handle_usuario():   

    if request.method == 'POST':
        _create_usuario()
        return {"message": "Usuario criado!"}, HTTPStatus.CREATED
    else:
        usuarios = _list_usuarios()
        lista_formatada = [{"id": u.id, "username": u.username,"role": {"id":u.role_id,"name": u.role.name}} for u in usuarios]
        return {"Usuarios": lista_formatada}, HTTPStatus.OK
    

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