import os
from flask import Flask, jsonify
from flask_caching import Cache
from sqlalchemy import text
from helpers.database import init_db, db
from models.cbo_sinonimos import Cbo_Sinonimos

app = Flask(__name__)
init_db(app)

cache = Cache(config={
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
    "CACHE_REDIS_PORT": os.getenv("REDIS_PORT", 6379),
    "CACHE_DEFAULT_TIMEOUT": 120
})
cache.init_app(app)

@app.route("/cbo/<codigo>")
@cache.cached()
def get_cbo(codigo):
    sql = text("SELECT * FROM cbo_sinonimos WHERE codigo = :codigo")
    result = db.session.execute(sql, {"codigo": codigo}).mappings().all()

    if not result:
        return jsonify({"erro": "Código não encontrado"}), 404

    return jsonify([dict(row) for row in result])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
