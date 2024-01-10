from flask import Blueprint

from .. import db, app

from .users.urls import usersBlueprint
from .settings.urls import settingsBlueprint

apiBlueprint = Blueprint('api', __name__)

apiBlueprint.register_blueprint(usersBlueprint, url_prefix='users')
apiBlueprint.register_blueprint(settingsBlueprint, url_prefix='settings')
