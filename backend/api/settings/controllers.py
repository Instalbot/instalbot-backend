import os

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from ..urls import db
from ..users.models import User, Word, Flag


def is_number(variable):
    return isinstance(variable, (int, float))


def xor_encryption(text, key):
    encrypted_text = ""

    for i in range(len(text)):
        encrypted_text += chr(ord(text[i]) ^ ord(key[i % len(key)]))

    return encrypted_text


def get_settings():
    try:
        userid = get_jwt_identity()

        user = db.session.query(User).filter_by(userid=userid).first()

        if user is None:
            return jsonify({'message': 'User does not exist', 'code': 401}), 401

        # Ensure flags and words exist, or create them
        if not user.flags:
            # Create default flags if they don't exist
            default_flags = Flag(todo=False, hoursrange="[14, 22]")
            user.flags.append(default_flags)

        if not user.words:
            # Create default words if they don't exist
            default_words = Word(list=[])
            user.words.append(default_words)

        db.session.commit()

        return jsonify({
            'message': 'OK!',
            'code': 200,
            'userid': userid,
            'flags': user.flags[0].to_dict(),
            'words': user.words[0].to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()  # Rollback changes if an exception occurs
        return jsonify({'message': 'Internal Server Error', 'code': 500}), 500


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

def update_instaling_login():
    request_json = request.get_json()
    userid = get_jwt_identity()

    if not request_json or 'login' not in request_json or 'password' not in request_json:
        return jsonify({'message': 'Invalid request format', 'code': 400}), 400

    login = request_json['login']
    password = request_json['password']

    user = db.session.query(User).filter_by(userid=userid).first()

    if user is None:
        return jsonify({'message': 'User does not exist', 'code': 401}), 401

    # Ensure the user updating the flags is the same as the one in the JWT
    if user.userid != userid:
        return jsonify({'message': 'Unauthorized to update user flags', 'code': 403}), 403

    hashed_password = xor_encryption(password, os.getenv('INSTALING_KEY'))

    flag_to_update = user.flags[0]
    flag_to_update.instaling_user = login
    flag_to_update.instaling_pass = hashed_password

    db.session.commit()

    return jsonify({'message': 'OK!', 'code': 200}), 200
