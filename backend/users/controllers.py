from flask import request, jsonify
from argon2 import PasswordHasher, profiles

from .models import User, Flag, Word
from .. import db


ph = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)

def create_user_controller():
    request_form = request.form.to_dict()
    username = request_form['username']
    email = request_form['email']
    password = request_form['password']

    if not username or not password or not email:
        return jsonify({
            "message": "Invalid request",
            "code": 400
        }), 400

    user = db.session.query(User).filter_by(email=email).first()

    if user:
        return jsonify({
            "message": "Email is taken",
            "code": 409
        }), 409

    hashed_password = ""

    try:
        hashed_password = ph.hash(password)
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

    flag = Flag(userid=new_user.userid)
    word = Word(userid=new_user.userid)

    db.session.add_all([flag, word])
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "code": 201,
    }), 201
