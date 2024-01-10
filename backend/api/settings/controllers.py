from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from ..urls import db
from ..users.models import User


def get_settings():
    userid = get_jwt_identity()

    user = db.session.query(User).filter_by(userid=userid).first()

    if user is None:
        return jsonify({
            'message': 'User does not exist',
            'code': 401
        })

    return jsonify({
        'message': 'OK!',
        'code': 200,
        'userid': userid,
        'flags': user.flags[0].to_dict(),
        'words': user.words[0].to_dict()
    }), 200
