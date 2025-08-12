import os
<<<<<<< HEAD
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
=======
import csv
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

def conexao_postgres():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def importar_csv():
    print("Iniciando importação do CSV...")
    try:
        conexao = conexao_postgres()
        if not conexao:
            print("Falha na conexão com o banco. Abortando importação.")
            return

        with conexao.cursor() as cursor, open("cbo2002-sinonimo.csv", "r", encoding="latin1") as f:
            leitor_csv = csv.reader(f, delimiter=";")
            next(leitor_csv)  # pula o cabeçalho

            for linha in leitor_csv:
                if len(linha) >= 2:
                    codigo, titulo = linha[0].strip(), linha[1].strip()
                    cursor.execute(
                        "INSERT INTO cbo (codigo, titulo) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (codigo, titulo)
                    )

        conexao.commit()
        print("Importação finalizada!")
    except Exception as e:
        print(f"Erro ao importar CSV: {e}")
    finally:
        if conexao:
            conexao.close()

@app.route("/dados/<codigo>")
def get_dado(codigo):
    
    titulo_cache = redis_client.get(codigo)
    if titulo_cache:
        return jsonify({"codigo": codigo, "titulo": titulo_cache, "origem": "redis"})

    conexao = conexao_postgres()
    if not conexao:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

    with conexao.cursor() as cursor:
        cursor.execute("SELECT titulo FROM cbo WHERE codigo = %s", (codigo,))
        resultado = cursor.fetchone()

    conexao.close()

    if resultado:
        titulo = resultado[0]
        redis_client.set(codigo, titulo)  # Salva no Redis
        return jsonify({"codigo": codigo, "titulo": titulo, "origem": "postgres"})
    else:
        return jsonify({"erro": "Código não encontrado"}), 404

if __name__ == "__main__":
    importar_csv()
    app.run(host="0.0.0.0", port=5000)
>>>>>>> ddbb873 (feat: ajustes finais)
