import os
import click 
import sqlalchemy as sa

from datetime import datetime
from flask import Flask, current_app
from src.db import db  # <-- Importa o db do seu arquivo db.py
from urllib.parse import quote_plus  # <-- Adicione essa importação lá no topo
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

migrate = Migrate()
jwt = JWTManager()


class Role(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    user: Mapped[list["Usuario"]] = relationship(back_populates="role")

    def __repr__(self) -> str:
       return f"Role(id={self.id!r}, name={self.username!r})"

class Usuario(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String, nullable=False)
    password: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("role.id"))
    role: Mapped['Role'] = relationship(back_populates='user')

    def __repr__(self) -> str:
       return f"User(id={self.id!r}, username={self.username!r}, active={self.active!r})"


class Post(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str]= mapped_column(sa.String, nullable=False)
    body: Mapped[str] = mapped_column(sa.String, nullable=False)
    created: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    author_id: Mapped[int]= mapped_column(sa.ForeignKey('usuario.id'))
    def __repr__(self) -> str:
       return f"Post(id={self.id!r}, title={self.title!r}, author_id{self.author_id!r})"

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    global db
    with current_app.app_context():
        db.create_all()
    click.echo('Initialized the database.')


def create_app(test_config=None):
    app = Flask(__name__)

    # 1. Tenta ler a URL completa do Render; se não achar, usa a local como padrão
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Se estiver rodando local, ele usa a sua senha padrão mascarada
        senha_protegida = quote_plus("snhus")    
        database_url = f'postgresql+psycopg://postgres:{senha_protegida}@127.0.0.1:5432/diobank'
       # 2. Agora sim, passe tudo para o mapping de forma limp
# 2. Configura o mapping de forma limpa
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"), # Também esconde a Secret Key!
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "uma-chave-padrao-local"),  
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    
       # Registrer cliec comamd
    app.cli.add_command(init_db_command)
     # Initialize extenstions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register Blueprints
    from src.controllers import usuario, post, auth, role


    app.register_blueprint(usuario.app)
    app.register_blueprint(post.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)

    return app