from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from db import db
from models import CouponModel
from schemas import CouponSchema

blp = Blueprint("Coupons", __name__, description="Operações com cupons")

@blp.route("/coupon")
class Coupon(MethodView):
    @jwt_required()
    @blp.arguments(CouponSchema)
    @blp.response(201, CouponSchema, description="Cupom criado com sucesso")
    def post(self, coupon_data):
        """ Rota para criar um cupom """
        current_user_id = get_jwt_identity()
        coupon = CouponModel(
            user_id=current_user_id,
            transaction_id=coupon_data['transaction_id'],
            code=coupon_data['code'],
            value=coupon_data['value']
        )
        db.session.add(coupon)
        db.session.commit()
        return coupon, 201

    @jwt_required()
    @blp.response(200, CouponSchema(many=True), description="Cupons do usuário")
    def get(self):
        """ Rota para listar os cupons de um usuário """
        current_user_id = get_jwt_identity()
        coupons = CouponModel.query.filter_by(user_id=current_user_id).all()
        return coupons, 200

    @jwt_required()
    @blp.arguments(CouponSchema)
    @blp.response(200, CouponSchema, description="Cupom atualizado com sucesso")
    def put(self, coupon_data):
        """ Rota para atualizar um cupom """
        current_user_id = get_jwt_identity()
        coupon = CouponModel.query.filter_by(user_id=current_user_id, id=coupon_data['id']).first()
        if not coupon:
            abort(404, message="Cupom não encontrado")

        coupon.transaction_id = coupon_data['transaction_id']
        coupon.code = coupon_data['code']
        coupon.value = coupon_data['value']

        db.session.commit()
        return coupon, 200

    @jwt_required()
    @blp.arguments(CouponSchema)
    @blp.response(204, description="Cupom removido com sucesso")
    def delete(self, coupon_data):
        """ Rota para remover um cupom """
        current_user_id = get_jwt_identity()
        coupon = CouponModel.query.filter_by(user_id=current_user_id, id=coupon_data['id']).first()
        if not coupon:
            abort(404, message="Cupom não encontrado")

        db.session.delete(coupon)
        db.session.commit()

        return None, 204
