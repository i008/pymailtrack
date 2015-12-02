from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username

    tc = db.relationship('TrackingCode', backref='user', lazy='dynamic')


class TrackingCode(db.Model):
    __tablename__ = 'trackingcode'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(), default='noinfo')
    recipient = db.Column(db.String(), default='noinfo')
    trackhash = db.Column(db.String())
    time = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    lr = db.relationship('Logs', backref='logs', lazy='dynamic')


class Logs(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer(), primary_key=True)
    code_id = db.Column(db.Integer(), db.ForeignKey('trackingcode.id'), nullable=False)
    ip = db.Column(db.String())
    time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    user_agent = db.Column(db.String())


