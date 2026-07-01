from http import HTTPStatus
from src.app import Usuario, Role  # <-- Certifique-se de importar o seu modelo Role aqui
from sqlalchemy import func
from src.db import db

def teste_get_usuario_success(client):
        # Cria a Role física primeiro para o SQLite saber que ela existe
        #Give (forneço para meu teste)
        role = Role(name="Admin")
        db.session.add(role)
        db.session.commit()        
        # Cria o usuário admin vinculado à Role acima        
        usuario = Usuario(            
            username="admin_teste",
            password="123",
            role_id=role.id  # Aponta perfeitamente para a Role ID 1
        )
        db.session.add(usuario)
        db.session.commit()  
    # Vamos usar o caminho direto com a barra caso sua rota precise dela
    #When (Executo)
        response = client.get(f"/usuarios/{usuario.id}")

    # 3. Valida o resultado
    #Then (Verifico)
        assert response.status_code == HTTPStatus.OK
        assert response.json == {"id": usuario.id,"username": usuario.username}

def teste_get_usuario_not_fount(client):
        # Cria a Role física primeiro para o SQLite saber que ela existe
        #Give (forneço para meu teste)
        role = Role(name="Admin")
        db.session.add(role)
        db.session.commit()        
        # Cria o usuário admin vinculado à Role acima        
        usuario_id = 1
     
    # Vamos usar o caminho direto com a barra caso sua rota precise dela
    #When (Executo)
        response = client.get(f"/usuarios/{usuario_id}")

    # 3. Valida o resultado
    #Then (Verifico)
        assert response.status_code == HTTPStatus.NOT_FOUND

def test_create_user(client, access_token):
        #Given
        role_id = db.session.execute(db.select(Role.id).where(Role.name == "Admin")).scalar()           
  
        playload = {"username": "user2",	"password": "tts","role_id": role_id}
           #When (Executo)
        response = client.post("/usuarios/", json = playload, headers={"Authorization": f"Bearer {access_token}"})
            #then (Verifica)
        assert response.status_code == HTTPStatus.CREATED
        assert response.json == {"message": "Usuario criado!"}
        assert db.session.execute(db.select(func.count(Usuario.id))).scalar() == 2


def test_list_users(client, access_token):
                # Cria a Role física primeiro para o SQLite saber que ela existe
        #Give (forneço para meu teste)
        usuario = db.session.execute(db.select(Usuario).where(Usuario.username == "admin_teste")).scalar()   

        response = client.post("/auth/login", json={"username": usuario.username, "password": usuario.password})
        access_token = response.json["access_token"]

        # 2. Faz a requisição enviando o Token no cabeçalho
        headers = {"Authorization": f"Bearer {access_token}"}
    
    # Vamos usar o caminho direto com a barra caso sua rota precise dela
        response = client.get("/usuarios/", headers=headers, follow_redirects=True)

        assert response.status_code == HTTPStatus.OK
        assert response.json == {
                "Usuarios":[
                        {
                                "id": usuario.id,
                                "username": usuario.username,
                                "role":{
                                        "id": usuario.role.id,
                                        "name": usuario.role.name,
                                },
                        }                        
                ]
        }