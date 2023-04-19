import os
import requests
from flask.views import MethodView
from flask_smorest import Blueprint
from .coupon_utils import create_coupon
from .transaction_utils import create_transaction
from schemas import PaymentSchema, CouponSchema, ExecutePaymentSchema
from models.transaction import TransactionModel

TransactionBlueprint = Blueprint('transaction', __name__)

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

@TransactionBlueprint.route('/process_payment', methods=['POST'])
class ProcessPayment(MethodView):
    @TransactionBlueprint.arguments(PaymentSchema, location="json")
    @TransactionBlueprint.response(201, CouponSchema, description="Pagamento processado com sucesso e cupom gerado.")
    @TransactionBlueprint.response(400, description="Falha no processamento de pagamento.")
    def post(self, payment_data):
        remaining_value = payment_data.get("remaining_value")
        user_data = payment_data.get("user_data")
        access_token = get_paypal_access_token()

        if not user_data or "user_id" not in user_data:
            return {"success": False, "data": "Dados do usuário não foram fornecidos."}, 400

        # lógica para processar o pagamento com o PayPal
        payment_amount = payment_data.get("amount")
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
                        "total": payment_amount,
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

        # Verificando se o pagamento foi bem-sucedido e processe as informações conforme necessário
        if payment_response.status_code == 201:
            user_id = user_data.get("user_id")

            # Obter o user_id e o transaction_id e Salve a transação no banco de dados
            transaction = create_transaction(user_id, payment_id, remaining_value)

            # Aprovação da URL para redirecionar o usuário
            approval_url = next((link["href"] for link in payment_response_data["links"] if link["rel"] == "approval_url"), None)

            if approval_url:
                return {"approval_url": approval_url}, 201
            else:
                return {"success": False, "data": "Falha no processamento de pagamento."}, 400


@TransactionBlueprint.route('/execute_payment', methods=['POST'])
class ExecutePayment(MethodView):
    @TransactionBlueprint.arguments(ExecutePaymentSchema, location="json")
    @TransactionBlueprint.response(200, description="Pagamento executado com sucesso.")
    @TransactionBlueprint.response(400, description="Falha na execução do pagamento.")
    def post(self, execute_data):
        payment_id = execute_data.get('payment_id')
        payer_id = execute_data.get('payer_id')

        if not payment_id or not payer_id:
            return {"error": "payment_id e payer_id são obrigatórios"}, 400

        access_token = get_paypal_access_token()

        # Executar o pagamento
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
                remaining_value = transaction.remaining_amount
                coupon = create_coupon(user_id, transaction_id, remaining_value)
                return {"success": True, "payment": execute_response_data, "coupon": coupon}, 200
            else:
                return {"error": "Transação não encontrada"}, 400
        else:
            return {"error": "Falha na execução do pagamento."}, 400
