import pytest
from src.app import create_app, db, Usuario, Role


@pytest.fixture#quando for fazer teste cuidado com o escopo
def app():
    app = create_app({
        "TESTING": True,  # Avisa o Flask que ele está em modo de teste
        "SECRET_KEY": "test",
        "JWT_SECRET_KEY": "uma-chave-secreta-longa-para-o-ambiente-de-testes",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # <-- Banco na memória RAM!
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

       # Cria as tabelas na memória antes do teste começar
    with app.app_context():
        db.create_all()

        yield app
    # Limpa tudo da memória após o término do teste
        db.drop_all()
    # clean up / reset resources here


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def access_token(client):
      
        role = Role(name="Admin")
        db.session.add(role)
        db.session.commit()        
               
        usuario = Usuario(            
            username="admin_teste",
            password="123",
            role_id=role.id 
        )
        db.session.add(usuario)
        db.session.commit()

        response = client.post("/auth/login", json={"username": usuario.username, "password": usuario.password})        
        return response.json["access_token"]  