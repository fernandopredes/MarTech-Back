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

class UserLoginSchema(Schema):
    """
    Define como deve ser a estrutura para realizar o login de um usuário.
    """
    email = fields.Email(required=True, description="e-mail do usuário")
    password = fields.Str(required=True, load_only=True, description="password do usuário")

    class Meta:
        description = "Define como um login de usuário deve ser representado"


class CreateUserSchema(Schema):
    """
    Define como deve ser a estrutura do dado após criação de usuário.
    """
    message = fields.String(description="Mensagem de usuário criado")

    class Meta:
        description = "Esquema de mensagem após a criação de usuário."

class UserTokenSchema(Schema):
    """
    Define como deve ser a estrutura do dado após um login.
    """
    access_token = fields.String(description="Token de acesso")
    user_id = fields.Int(description="Id do usuário")

    class Meta:
        description = "Esquema para resposta da rota de login do usuário"

#schemas para trasaction.py
class UserDataSchema(Schema):
    user_id = fields.Integer(required=True)

class PaymentSchema(Schema):
    remaining_value = fields.Float(required=True)
    user_data = fields.Nested(UserDataSchema, required=True)
    amount = fields.Float(required=True)

class CouponSchema(Schema):
    code = fields.String(required=True)
    value = fields.Float(required=True)

#schemas para payment
class ExecutePaymentSchema(Schema):
    payer_id = fields.String(required=True)
    payment_id = fields.String(required=True)
