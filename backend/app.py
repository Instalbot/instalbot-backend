import os
import threading

from flask import jsonify
from flask_jwt_extended import JWTManager
from . import create_app, jwt
from .api import urls
import redis

app = create_app(os.getenv('CONFIG_MODE') or 'development')

r = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
    db=0
)
t = r.client_id()

pubsub = r.pubsub()
pubsub.subscribe('workers_finished')


@jwt.expired_token_loader
def my_expired_token_callback(_, expired_token):
    token_type = expired_token['type']
    return jsonify({
        'message': 'The {} token has expired'.format(token_type),
        'code': 401
    }), 401


@jwt.invalid_token_loader
def my_invalid_token_callback(_):
    return jsonify({
        'message': 'Token is invalid',
        'code': 401
    }), 401

@jwt.unauthorized_loader
def my_unauthorized_loader_callback(_):
    return jsonify({
        'message': 'Unauthorized',
        'code': 401
    }), 401


@app.errorhandler(404)
def not_found(_):
    return jsonify({
        'message': 'Requested resource was not found',
        'code': 404
    }), 404


@app.errorhandler(500)
def internal_server_error(_):
    return jsonify({
        'message': 'Internal server error',
        'code': 500
    }), 500


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({
        'message': 'Method Not Allowed',
        'code': 405
    }), 405


@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello, backend is working',
        'code': 200,
    }), 200


app.register_blueprint(urls.apiBlueprint, url_prefix='/api')

listener = False

def listen_for_messages():
    global listener
    listener = True
    for message in pubsub.listen():
        if message['type'] == 'message':
            splitted = str(message['data']).split("-")
            emitter = splitted[0]
            event_type = splitted[1]
            worker_id = splitted[2]
            user_id = splitted[3]

            if emitter == 'SCRAPER':
                if int(worker_id) == t:
                    print(f"Receiver {event_type} scraping task for {user_id}!")

if not listener:
    threading.Thread(target=listen_for_messages).start()
