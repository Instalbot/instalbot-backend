from flask import request, jsonify

from ..app import app
from .controllers import create_user_controller

method_not_allowed = {
    'message': 'Method Not Allowed',
    'code': 405
}

@app.route('/users', methods=['POST'])
def list_create_accounts():
    if request.method == 'POST': return create_user_controller()
    else: return jsonify(method_not_allowed)
