from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import NUMRANGE
from psycopg2.extras import NumericRange
from sqlalchemy.orm import relationship
from argon2 import PasswordHasher, profiles, exceptions as HashingExceptions

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:1234@127.0.0.1:5432/instalbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ph = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)


class User(db.Model):
    __tablename__ = 'users'

    userid = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    flags = relationship('Flag', backref='user', lazy=True)
    words = relationship('Word', backref='user', lazy=True)

    def __json__(self):
        return dict({'username': self.username, 'email': self.email, 'userid': self.userid})

    def check_password(self, password):
        try:
            fine = ph.verify(self.password, password)
        except HashingExceptions:
            fine = False

        return fine


class Flag(db.Model):
    __tablename__ = 'flags'

    userid = db.Column(db.ForeignKey('users.userid'), primary_key=True)
    todo = db.Column(db.Boolean, server_default=db.FetchedValue())
    hoursrange = db.Column(NUMRANGE, server_default=db.FetchedValue())

    def __init__(self, userid, todo=False, hoursrange=NumericRange(14, 24)):
        self.userid = userid
        self.todo = todo
        self.hoursrange = hoursrange


class Word(db.Model):
    __tablename__ = 'words'

    userid = db.Column(db.ForeignKey('users.userid'), primary_key=True)
    list = db.Column(db.JSON, nullable=False)

    def __init__(self, userid, word_list=[]):
        self.userid = userid
        self.list = word_list


@app.errorhandler(404)
def not_found(_):
    return jsonify({
        "message": "Requested resource was not found",
        "status": 404
    }), 404


@app.route("/")
def index():
    return jsonify({
        "message": "Hello, backend is working",
        "status": 200,
    })


@app.route("/api/v1/user/register", methods=['POST'])
def user_register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    user = db.session.query(User).filter_by(email=email).first()

    if user:
        return jsonify({
            "message": "Email is taken",
            "status": 409
        })

    try:
        hashed_password = ph.hash(password)
    except HashingExceptions.HashingError:
        return jsonify({
            "message": "Encountered an error while hashing password",
            "status": 500
        })

    user = User(username=username, password=hashed_password, email=email)
    db.session.add(user)
    db.session.commit()

    flag = Flag(userid=user.userid)
    word = Word(userid=user.userid)

    db.session.add_all([flag, word])
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "status": 201,
        "user": user.__json__()
    })


@app.route("/api/v1/user/login", methods=['POST'])
def user_login():
    email = request.form['email']
    password = request.form['password']

    user = db.session.query(User).filter_by(email=email).first()

    invalid_password = jsonify({
        "message": "Invalid username or password",
        "status": 401
    })

    if not user:
        return invalid_password, 401

    if not user.check_password(password):
        return invalid_password, 401

    return jsonify({
        "message": "Logged in successfully",
        "status": 200,
        "user": user.__json__()
    })
