import os

class Config:
    TESTING = False 
    DEBUG = False    
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("database_url")

class ProductionConfig(Config):
    pass
#para rodar usar esse comando: 
#ENVIROMENT=production DATABASE_URL="postgresql+psycopg://postgres:SUA_SENHA_AQUI@127.0.0.1:5432/diobank" poetry run flask --app src.app run


class DevelopmentConfig(Config):
    SECRET_KEY = "dev"
    DEBUG = True
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://postgres:snhus@127.0.0.1:5432/diobank'
    
class TestingConfig(Config):
    TESTING =  True  # Avisa o Flask que ele está em modo de teste
    DEBUG = True
    SECRET_KEY =  "test"
    JWT_SECRET_KEY = "uma-chave-secreta-longa-para-o-ambiente-de-testes"
    SQLALCHEMY_DATABASE_URI =  "sqlite:///:memory:"  # <-- Banco na memória RAM!
        