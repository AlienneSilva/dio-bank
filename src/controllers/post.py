from flask import Blueprint, request
from src.app import Post, db
from http import HTTPStatus
from sqlalchemy import inspect

app = Blueprint('post', __name__, url_prefix="/posts")


def _create_post():
    data = request.json
    
    # Criamos APENAS UM usuário com todos os dados juntos
    novo_post = Post(
        title=data["title"],
        body=data["body"],
        author_id=data["author_id"]
    )
    
    # Adicionamos esse único usuário na sessão
    db.session.add(novo_post)
    db.session.commit()

def _list_post():
    query = db.select(Post)
    results = db.session.execute(query).scalars().all()
    return results

@app.route('/', methods=['GET', 'POST'])
def handle_post():
    if request.method == 'POST':
        _create_post()
        return {"message": "Postagem criada!"}, HTTPStatus.CREATED
    else:
        posts = _list_post()
        
        # Correção: Acessando os atributos corretos do modelo Post (title, body, author_id)
        lista_formatada = [
            {
                "id": p.id, 
                "title": p.title, 
                "body": p.body, 
                "author_id": p.author_id
            } for p in posts
        ]
        
        return {"Posts": lista_formatada}, HTTPStatus.OK
        
@app.route('/<int:post_id>')
def get_post(post_id):
    post = db.get_or_404(Post, post_id)
    return {        
        "id": post.id, 
        "title": post.title,
        "body": post.body,
        "author_id": post.author_id
    }

@app.route('/<int:post_id>', methods=["PATCH"])  # PUT = atualiza todos os campos // PATH = atualiza somente o campo solitado 
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    data = request.json   

    mapper =  inspect(Post)
    for column in mapper.attrs:
        if column.key in data:
            setattr(post, column.key, data[column.key])
    db.session.commit()


    return {        
        "id": post.id, 
        "title": post.title,
        "body": post.body,
        "author_id": post.author_id
    }

@app.route('/<int:post_id>', methods=["DELETE"])
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()

    return "", HTTPStatus.NO_CONTENT