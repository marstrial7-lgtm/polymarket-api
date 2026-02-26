from flask import Flask, request, jsonify
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import os

app = Flask(__name__)

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FUNDER = os.getenv("FUNDER_ADDRESS")
API_KEY = os.getenv("CLOB_API_KEY")
SECRET = os.getenv("CLOB_SECRET")
PASSPHRASE = os.getenv("CLOB_PASSPHRASE")

def get_client():
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,
        funder=FUNDER
    )
    client.set_api_creds({
        "apiKey": API_KEY,
        "secret": SECRET,
        "passphrase": PASSPHRASE
    })
    return client

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        client = get_client()
        balance = client.get_balance()
        return jsonify({"balance": balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/markets', methods=['GET'])
def get_markets():
    try:
        client = get_client()
        markets = client.get_markets()
        return jsonify({"markets": markets})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/order', methods=['POST'])
def place_order():
    try:
        data = request.json
        token_id = data.get('token_id')
        amount = float(data.get('amount'))
        side = BUY if data.get('side', 'BUY').upper() == 'BUY' else SELL

        client = get_client()
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
            side=side,
            order_type=OrderType.FOK
        )
        signed_order = client.create_market_order(order_args)
        resp = client.post_order(signed_order, OrderType.FOK)
        return jsonify({"result": resp})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/positions', methods=['GET'])
def get_positions():
    try:
        client = get_client()
        positions = client.get_positions()
        return jsonify({"positions": positions})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
