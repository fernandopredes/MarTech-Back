from db import db
from models.user_items import user_items
from models.coupon import CouponModel
from models.transaction import TransactionModel

class UserModel(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    coupons = db.relationship('CouponModel', backref='user', lazy=True)
    items = db.relationship('ItemModel', secondary=user_items, backref=db.backref('users', lazy=True))
    transactions = db.relationship('TransactionModel', backref='user', lazy=True)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
