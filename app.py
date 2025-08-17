import os
import csv
import json
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

# Variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

CACHE_KEY_ALL = "cbo:all"

# Cliente Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)


def conexao_postgres():
    """Cria uma conexão com o banco Postgres"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None


def importar_csv():
    """Importa dados do CSV para o banco (executar apenas uma vez se necessário)."""
    print("Iniciando importação do CSV...")
    conexao = None
    try:
        conexao = conexao_postgres()
        if not conexao:
            print("Falha na conexão com o banco. Abortando importação.")
            return

        with conexao.cursor() as cursor, open("cbo2002-ocupacao.csv", "r", encoding="latin1") as f:
            leitor_csv = csv.reader(f, delimiter=";")
            next(leitor_csv)  # pula cabeçalho

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


@app.route("/dados")
def get_todos_dados():
    """Retorna todos os registros do banco (com cache em Redis)."""

    # Primeiro tenta pegar do cache
    cache = redis_client.get(CACHE_KEY_ALL)
    if cache:
        return jsonify({"dados": json.loads(cache), "origem": "redis"})

    # Se não tiver no cache, pega do banco
    conexao = conexao_postgres()
    if not conexao:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT codigo, titulo FROM cbo")
            resultados = cursor.fetchall()
            dados = [{"codigo": row[0], "titulo": row[1]} for row in resultados]

        # Salva a lista no Redis com TTL de 5 minutos
        redis_client.setex(CACHE_KEY_ALL, 300, json.dumps(dados))

        return jsonify({"dados": dados, "origem": "postgres"})
    finally:
        conexao.close()


@app.route("/dados/<codigo>")
def get_dado(codigo):
    """Retorna um registro específico pelo código (com cache em Redis)."""

    # Primeiro tenta pegar do cache
    titulo_cache = redis_client.get(codigo)
    if titulo_cache:
        return jsonify({"codigo": codigo, "titulo": titulo_cache, "origem": "redis"})

    # Se não tiver no cache, pega do banco
    conexao = conexao_postgres()
    if not conexao:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT titulo FROM cbo WHERE codigo = %s", (codigo,))
            resultado = cursor.fetchone()

        if resultado:
            titulo = resultado[0]
            redis_client.setex(codigo, 300, titulo)  # salva com TTL de 5 min
            return jsonify({"codigo": codigo, "titulo": titulo, "origem": "postgres"})
        else:
            return jsonify({"erro": "Código não encontrado"}), 404
    finally:
        conexao.close()


# Só roda importar_csv() se o arquivo existir
if __name__ == "__main__":
    #if os.path.exists("cbo2002-ocupacao.csv"):
    importar_csv()
    app.run(host="0.0.0.0", port=5000)
