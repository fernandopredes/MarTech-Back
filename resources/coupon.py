from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models import CouponModel
from schemas import CouponSchema, CouponsSchema

CouponBlueprint = Blueprint("Coupons", __name__, description="Operações com cupons")

@CouponBlueprint.route('/coupons/user/<int:user_id>')
class CouponsByUser(MethodView):
    def get(self, user_id):
        """ Rota para obter cupons por ID de usuário """
        coupons = CouponModel.query.filter_by(user_id = user_id).all()
        if coupons:
            return {"coupon": CouponSchema().dump(coupons, many = True)}, 200
        else:
            abort(404, message="Nenhum cupom encontrado para este usuário.")

@CouponBlueprint.route('/coupons')
class AllCoupons(MethodView):
    def get(self):
        """ Rota para obter todos os cupons """
        coupons = CouponModel.query.all()
        if coupons:
            return {"coupons": CouponsSchema().dump(coupons, many=True)}, 200
        else:
            abort(404, message="Nenhum cupom encontrado.")
