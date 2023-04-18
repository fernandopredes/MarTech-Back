from db import db

class TransactionModel(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_id = db.Column(db.String(255), nullable=False)
    remaining_amount = db.Column(db.Numeric(10, 2), nullable=False)
