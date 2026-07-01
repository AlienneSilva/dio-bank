import psycopg
from psycopg.rows import dict_row
from flask import current_app, g
import click

from flask_sqlalchemy import SQLAlchemy

# Instancia o SQLAlchemy aqui para poder importar nos modelos e rotas
db = SQLAlchemy()

def get_db():
    if 'db' not in g:
        # Conecta ao PostgreSQL usando a string que configuramos no __init__.py
        # E já ativa o dict_row para aceitar a busca por nome de coluna!
        g.db = psycopg.connect(
            current_app.config['DATABASE'],
            row_factory=dict_row
        )
    return g.db

def close_db(e=None):
    # Remove o banco do contexto 'g' e fecha a conexão se ela existir
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # No PostgreSQL, precisamos do cursor para rodar comandos
    cursor = db.cursor()

    # Abrimos o arquivo schema.sql (repare que tirei o .decode('utf8') 
    # porque abrir com a propriedade encoding='utf-8' já resolve e é mais limpo)
    with current_app.open_resource('schema.sql', mode='r', encoding='utf-8') as f:
        # Executamos o conteúdo do arquivo usando o cursor
        cursor.execute(f.read())
    
   
    db.commit()
    cursor.close()



def init_app(app):
    app.teardown_appcontext(close_db)
    

