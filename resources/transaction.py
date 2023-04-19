import os
import requests
from decimal import Decimal
from flask.views import MethodView
from flask_smorest import Blueprint
from .coupon_utils import create_coupon
from .transaction_utils import create_transaction
from schemas import PaymentSchema, CouponSchema, ExecutePaymentSchema
from models.transaction import TransactionModel
from models.user import UserModel

TransactionBlueprint = Blueprint('Transaction', __name__, description="Operações de transição com o PayPal")

# Configuração do PayPal
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

# Função para obter um token de acesso do PayPal
def get_paypal_access_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    auth = (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, auth=auth, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# End-point para realizar a primeira parte da transição para o PAYPAL
@TransactionBlueprint.route('/process_payment')
class ProcessPayment(MethodView):
    @TransactionBlueprint.arguments(PaymentSchema, location="json")
    @TransactionBlueprint.response(201, CouponSchema, description="Pagamento processado e gerada a url de pagamento.")
    @TransactionBlueprint.response(400, description="Falha no processamento de pagamento.")
    def post(self, payment_data):
        """ Rota para mandar os dados e gerar url de pagamento """
        remaining_value = payment_data.get("remaining_value")
        user_data = payment_data.get("user_data")
        access_token = get_paypal_access_token()

        #Pega os dados enviados em user_data e verifica se ele existe
        if not user_data or "user_id" not in user_data:
            return {"success": False, "data": "Dados do usuário não foram fornecidos."}, 400

        user_id = user_data.get("user_id")
        user = UserModel.find_by_id(user_id)

        # Validação para que o remaining_value seja menor do que o amount passado pelo usuário
        if remaining_value <= 0 or remaining_value >= user.amount:
            return {"success": False, "data": "O valor deve ser menor ou igual ao total na conta."}, 400

        # Validação para verificar se o usuárioe xiste
        if not user:
            return {"success": False, "data": "Usuário não encontrado."}, 400

        # Coloca o valor do pagamento como a subtração entre o total do usuario menos o que sobrou
        payment_amount = user.amount - Decimal(remaining_value)

        # lógica para processar o pagamento com o PayPal
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [
                {
                    "amount": {
                        "total": str(payment_amount),
                        "currency": "BRL"
                    },
                    "description": "Pagamento do evento"
                }
            ],
            "redirect_urls": {
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel"
            }
        }

        payment_url = "https://api-m.sandbox.paypal.com/v1/payments/payment" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com/v1/payments/payment"
        payment_response = requests.post(payment_url, json=payment_data, headers=headers)
        payment_response_data = payment_response.json()

        payment_id = payment_response_data.get("id")
        if not payment_id:
            return {"success": False, "data": "Falha no processamento de pagamento."}, 400

        # Verificando se o pagamento funcionou corretamente
        if payment_response.status_code == 201:

            # Pega o user_id para criar  uma transaction
            user_id = user_data.get("user_id")

            # Salva a transação no banco de dados com os seus dados
            transaction = create_transaction(user_id, payment_id, payment_amount)

            # Aprova a URL para redirecionar o usuário
            approval_url = next((link["href"] for link in payment_response_data["links"] if link["rel"] == "approval_url"), None)

            if approval_url:
                return {"approval_url": approval_url}, 201
            else:
                return {"success": False, "data": "Falha no processamento de pagamento."}, 400


@TransactionBlueprint.route('/execute_payment')
class ExecutePayment(MethodView):
    @TransactionBlueprint.arguments(ExecutePaymentSchema, location="json")
    @TransactionBlueprint.response(200, description="Pagamento executado com sucesso e cupom criado.")
    @TransactionBlueprint.response(400, description="Falha na execução do pagamento.")
    def post(self, execute_data):
        """ Rota para confirmar o pagamento e gerar o cupom """
        payment_id = execute_data.get('payment_id')
        payer_id = execute_data.get('payer_id')

        if not payment_id or not payer_id:
            return {"error": "payment_id e payer_id são obrigatórios"}, 400

        access_token = get_paypal_access_token()

        # Executar o pagamento no molde do PAYPAL
        execute_url = f'https://api-m.sandbox.paypal.com/v1/payments/payment/{payment_id}/execute' if PAYPAL_MODE == "sandbox" else f'https://api-m.paypal.com/v1/payments/payment/{payment_id}/execute'
        execute_payload = {
            "payer_id": payer_id
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        execute_response = requests.post(execute_url, json=execute_payload, headers=headers)
        execute_response_data = execute_response.json()

        if execute_response.status_code == 200:
            # O pagamento foi executado com sucesso
            transaction = TransactionModel.find_by_payment_id(payment_id)
            if transaction:
                user_id = transaction.user_id
                transaction_id = transaction.id
                user = UserModel.find_by_id(user_id)
                if user:
                    # Cálculo para colocar apenas o valor restante no coupon
                    remaining_value = user.amount - transaction.payment_amount
                    # Tratativa para o caso do valor restante ser menor ou igual a zero e não seja possivel criar um coupon
                    if remaining_value > 0:
                        coupon = create_coupon(user_id, transaction_id, remaining_value)
                    else:
                        coupon = "O valor restante não é suficiente para criar um cupom."
                return {"success": True, "payment": execute_response_data, "coupon": coupon}, 200

            else:
                return {"error": "Transação não encontrada"}, 400
        else:
            return {"error": "Falha na execução do pagamento."}, 400
