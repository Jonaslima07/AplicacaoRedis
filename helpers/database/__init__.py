import os
from flask_sqlalchemy import SQLAlchemy

try:
    db = SQLAlchemy()

    def init_db(app):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        
except Exception as e:
    print("Erro ao tentar conectar ao banco de dados", e)