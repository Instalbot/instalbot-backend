from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from .controllers import get_settings, update_settings

settingsBlueprint = Blueprint('settings', __name__)


@settingsBlueprint.route('/', methods=['GET', 'PUT'])
@jwt_required()
def handle_settings():
    if request.method == 'GET':
        return get_settings()
    elif request.method == 'PUT':
        return update_settings()
