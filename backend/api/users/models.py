from sqlalchemy.dialects.postgresql import JSON, NUMRANGE
from datetime import datetime

from ..urls import db
from .password_hasher import verify_password


class User(db.Model):
    __tablename__ = 'users'

    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    # Define the relationship with the Flags table
    flags = db.relationship('Flag', backref='user', cascade='all, delete-orphan', single_parent=True)

    # Define the relationship with the Words table
    words = db.relationship('Word', backref='user', cascade='all, delete-orphan', single_parent=True)

    def verify_password(self, password):
        return verify_password(password, self.password)

    def __repr__(self):
        return '<User %r>' % self.email

    def to_dict(self):
        return {
            'userid': self.userid,
            'username': self.username,
            'email': self.email,
            'flags': self.flags.to_dict(),
            'words': self.words.to_dict()
        }


class Flag(db.Model):
    __tablename__ = 'flags'

    userid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete='CASCADE'), primary_key=True)
    todo = db.Column(db.Boolean, default=False)
    hoursrange = db.Column(NUMRANGE, default='[14, 22]')

    def __repr__(self):
        return '<Flag %r>' % self.userid

    def to_dict(self):
        return {
            'userid': self.userid,
            'todo': self.todo,
            'hoursrange': self.hoursrange
        }


class Word(db.Model):
    __tablename__ = 'words'

    userid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete='CASCADE'), primary_key=True)
    list = db.Column(JSON, nullable=False, default=[])

    def __repr__(self):
        return '<Word %r>' % self.userid

    def to_dict(self):
        return {
            'userid': self.userid,
            'list': self.list
        }
