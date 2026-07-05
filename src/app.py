import os

from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from src.db import db  # <-- Importa o db do seu arquivo db.py
from src.models import db
from urllib.parse import quote_plus  # <-- Adicione essa importação lá no topo

bcrypt = Bcrypt()

migrate = Migrate()
jwt = JWTManager()

def create_app(enviroment=os.environ["ENVIROMENT"]):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(f"src.config.{enviroment.title()}Config")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 1. Tenta ler a URL completa do Render; se não achar, usa a local como padrão
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Se estiver rodando local, ele usa a sua senha padrão mascarada
        senha_protegida = quote_plus("snhus")    
        database_url = f'postgresql+psycopg://postgres:{senha_protegida}@127.0.0.1:5432/diobank'
 

     # Initialize extenstions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    from src.controllers import usuario, post, auth, role


    app.register_blueprint(usuario.app)
    app.register_blueprint(post.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)

    return app