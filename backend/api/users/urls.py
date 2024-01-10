from flask import Blueprint

from .controllers import create_user_controller, login_user_controller

usersBlueprint = Blueprint('users', __name__)


@usersBlueprint.post('/register')
def users_register():
    return create_user_controller()


@usersBlueprint.post('/login')
def users_login():
    return login_user_controller()
