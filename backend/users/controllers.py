from flask import request, jsonify
from argon2 import PasswordHasher, profiles

from .models import User, Flag, Word
from .. import db


ph = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)

def create_user_controller():
    request_form = request.form.to_dict()
    email = request_form['email']
    username = request_form['username']

    user = db.session.query(User).filter_by(email=email).first()

    if user:
        return jsonify({
            "message": "Email is taken",
            "code": 409
        }), 409

    hashed_password = ""

    try:
        hashed_password = ph.hash(request_form['password'])
    except Exception as e:
        return jsonify({
            "message": "Encountered an error while hashing password",
            "code": 500
        }), 500

    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    flag = Flag(userid=user.userid)
    word = Word(userid=user.userid)

    db.session.add_all([flag, word])
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "code": 201,
    }), 201
