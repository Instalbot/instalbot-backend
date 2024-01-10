from flask import request, jsonify
from flask_jwt_extended import create_access_token

from .models import User, Flag, Word
from .password_hasher import hash_password
from ..urls import db


def create_user_controller():
    request_form = request.form.to_dict()

    if not ('username' in request_form and 'password' in request_form and 'email' in request_form):
        return jsonify({
            'message': 'Invalid request',
            'code': 400
        }), 400

    username = request_form['username']
    email = request_form['email']
    password = request_form['password']

    user = db.session.query(User).filter_by(email=email).first()

    if user:
        return jsonify({
            'message': 'Email is taken',
            'code': 409
        }), 409

    hashed_password = hash_password(password)

    if hashed_password is None:
        return jsonify({
            'message': 'Encountered an error while hashing password',
            'code': 500
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
        'message': 'User registered successfully',
        'code': 201,
    }), 201


def login_user_controller():
    request_form = request.form.to_dict()

    if not ('password' in request_form and 'email' in request_form):
        return jsonify({
            'message': 'Invalid request',
            'code': 400
        }), 400

    email = request_form['email']
    password = request_form['password']

    user = db.session.query(User).filter_by(email=email).first()

    if not user or not user.verify_password(password):
        return jsonify({
            'message': 'Invalid password or email address',
            'code': 401
        }), 401

    payload = create_access_token(identity=user.userid)

    return jsonify({'message': 'OK', 'code': 200, 'token': payload})
