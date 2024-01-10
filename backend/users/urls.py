from flask import Blueprint

from .controllers import create_user_controller, login_user_controller

users = Blueprint('users', __name__)


@users.post('/register')
def users_register():
    return create_user_controller()


@users.post('/login')
def users_login():
    return login_user_controller()
