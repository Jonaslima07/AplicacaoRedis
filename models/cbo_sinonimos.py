from flask_restful import fields
from helpers.database import db

cbo_sinonimos_fields = {
    "id": fields.Integer,
    "codigo" : fields.Integer,
    "titulo": fields.String
}


class Cbo_Sinonimos(db.Model):
    __tablename__ = "cbo_sinonimos"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    titulo = db.Column(db.Text, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)

    def __init__(self, codigo, titulo):
       self.codigo = codigo,
       self.titulo = titulo