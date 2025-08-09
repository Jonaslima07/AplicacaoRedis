from flask_restful import Api
from flask import Blueprint

from resoucers.cbo_ocupacao import Cbo_ocupacao


blueprint = Blueprint('api', __name__)

api = Api()

api.add_resource(Cbo_ocupacao, "/cbo_ocupacao")
#api.add_resource(Cbo_ocupacao_solr, "/cbo_ocupacao_solr/<string:busca>")
