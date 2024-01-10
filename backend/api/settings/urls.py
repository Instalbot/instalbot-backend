from flask import Blueprint
from flask_jwt_extended import jwt_required
from .controllers import get_settings

settingsBlueprint = Blueprint('settings', __name__)


@settingsBlueprint.get('/')
@jwt_required()
def index():
    return get_settings()
