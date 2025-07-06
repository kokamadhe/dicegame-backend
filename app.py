from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import stripe
import os

app = Flask(__name__)
CORS(app)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route("/roll", methods=["POST"])
def roll_dice():
    data = request.get_json()
    target = data.get("target")
    amount = float(data.get("amount", 0))

    if not (1 <= target <= 95):
        return jsonify({"error": "Invalid target"}), 400

    roll = random.randint(1, 100)
    win = roll < target
    payout = round(amount * (95 / target), 2) if win else 0

    return jsonify({
        "roll": roll,
        "win": win,
        "payout": payout
    })

@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    data = request.get_json()
    amount = int(data.get("amount", 0)) * 100  # Convert to cents

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )
        return jsonify({"clientSecret": intent.client_secret})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
