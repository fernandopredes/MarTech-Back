import random
import string
from models.coupon import CouponModel
from db import db

def generate_coupon_code(length=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def create_coupon(user_id, transaction_id, value):
    coupon_code = generate_coupon_code()
    coupon = CouponModel(user_id=user_id, transaction_id=transaction_id, code=coupon_code, value=value)
    db.session.add(coupon)
    db.session.commit()
    return {
        "id": coupon.id,
        "user_id": coupon.user_id,
        "transaction_id": coupon.transaction_id,
        "code": coupon.code,
        "value": str(coupon.value)
    }
