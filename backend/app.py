import os
from flask import jsonify
from flask_jwt_extended import JWTManager
from . import create_app, jwt
from .api import urls

app = create_app(os.getenv('CONFIG_MODE') or 'development')


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


if __name__ == '__main__':
    app.run()
