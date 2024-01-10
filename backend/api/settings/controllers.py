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
    try:
        request_json = request.get_json()
        userid = get_jwt_identity()

        if not request_json or 'flags' not in request_json:
            return jsonify({'message': 'Invalid request format', 'code': 400}), 400

        flags = request_json['flags']

        if 'hoursrange' not in flags or 'lower' not in flags['hoursrange'] or 'upper' not in flags['hoursrange']:
            return jsonify({'message': 'Invalid hoursrange format', 'code': 400}), 400

        lower = flags['hoursrange']['lower']
        upper = flags['hoursrange']['upper']

        if not is_number(lower) or not is_number(upper):
            return jsonify({'message': 'Invalid number format in hoursrange', 'code': 400}), 400

        user = db.session.query(User).filter_by(userid=userid).first()

        if user is None:
            return jsonify({'message': 'User does not exist', 'code': 401}), 401

        # Ensure the user updating the flags is the same as the one in the JWT
        if user.userid != userid:
            return jsonify({'message': 'Unauthorized to update user flags', 'code': 403}), 403

        flag_to_update = user.flags[0]
        flag_to_update.hoursrange = "[{}, {}]".format(lower, upper)

        db.session.commit()

        return jsonify({'message': 'OK!', 'code': 200}), 200

    except Exception as e:
        return jsonify({'message': 'Internal Server Error', 'code': 500}), 500
