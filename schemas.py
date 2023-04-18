from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True, description="id do usuário")
    name = fields.Str(required=True, description="nome do usuário")
    email = fields.Email(required=True, description="e-mail do usuário")
    password = fields.Str(required=True, load_only=True, description="senha do usuário")

    class Meta:
        description = "Define a estrutura de um usuário"

class ItemSchema(Schema):
    id = fields.Int(dump_only=True, description="id do item")
    name = fields.Str(required=True, description="nome do item")
    description = fields.Str(required=True, description="descrição do item")

    class Meta:
        description = "Define a estrutura de um item"

class CouponSchema(Schema):
    id = fields.Int(dump_only=True, description="id do cupom")
    user_id = fields.Int(required=True, description="id do usuário")
    transaction_id = fields.Int(required=True, description="id da transação")
    code = fields.Str(required=True, description="código do cupom")
    value = fields.Decimal(required=True, as_string=True, description="valor do cupom")

    class Meta:
        description = "Define a estrutura de um cupom"

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True, description="id da transação")
    user_id = fields.Int(required=True, description="id do usuário")
    payment_id = fields.Str(required=True, description="id do pagamento")
    remaining_amount = fields.Decimal(required=True, as_string=True, description="valor restante")

    class Meta:
        description = "Define a estrutura de uma transação"
