import os
from flask import jsonify
from . import create_app

app = create_app(os.getenv('CONFIG_MODE') or 'development')


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

# Import all paths
from .users import urls

if __name__ == '__main__':
    app.run()
