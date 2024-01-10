from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from ..urls import db
from ..users.models import User


def is_number(variable):
    return isinstance(variable, (int, float))


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


def update_settings():
    request_form = request.json
    userid = get_jwt_identity()

    invalid_request = jsonify({
        'message': 'Invalid request',
        'code': 400
    }), 400

    if 'flags' not in request_form:
        return invalid_request

    flags = request_form['flags']

    if 'hoursrange' not in flags:
        return invalid_request

    hoursrange = flags['hoursrange']

    if not ('lower' in hoursrange and 'upper' in hoursrange) or not is_number(hoursrange['lower']) or not is_number(hoursrange['upper']):
        return invalid_request

    user = db.session.query(User).filter_by(userid=userid).first()

    if user is None:
        return jsonify({
            'message': 'User does not exist',
            'code': 401
        })

    flag_to_update = user.flags[0]

    flag_to_update.hoursrange = "[{}, {}]".format(hoursrange['lower'], hoursrange['upper'])

    db.session.commit()

    return jsonify({
        'message': 'OK!',
        'code': 200
    }), 200
