from db import db

class CouponModel(db.Model):
    __tablename__ = 'coupon'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)

    transaction = db.relationship('Transaction', backref=db.backref('coupon', uselist=False))
