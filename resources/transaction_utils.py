from models.transaction import TransactionModel
from db import db

def create_transaction(user_id, payment_id, remaining_amount):
    transaction = TransactionModel(user_id=user_id, payment_id=payment_id, remaining_amount=remaining_amount)
    db.session.add(transaction)
    db.session.commit()

    return transaction
