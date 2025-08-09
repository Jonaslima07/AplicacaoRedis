from flask import Flask, jsonify
from flask_caching import Cache

app = Flask(__name__)
cache = Cache()

app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 120

cache.init_app(app)

@app.route('/api/data')
@cache.cached()
def get_data():
    data = {'name': 'your_name'}
    return jsonify(data)

if __name__ == '__main__':
    app.run()