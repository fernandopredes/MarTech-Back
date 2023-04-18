from db import db
from models.user_items import user_items

class UserModel(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    coupons = db.relationship('Coupon', backref='user', lazy=True)
    items = db.relationship('Item', secondary=user_items, backref=db.backref('users', lazy=True))
    transactions = db.relationship('Transaction', backref='user', lazy=True)
