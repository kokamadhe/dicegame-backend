from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import stripe
import os

app = Flask(__name__)
CORS(app)

# Load Stripe secret key from environment variable
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Dice roll endpoint
@app.route("/roll", methods=["POST"])
def roll_dice():
    data = request.get_json()
    target = data.get("target")
    amount = float(data.get("amount", 0))

    if not (1 <= target <= 95):
        return jsonify({"error": "Invalid target number"}), 400

    roll = random.randint(1, 100)
    win = roll < target
    payout = round(amount * (95 / target), 2) if win else 0

    return jsonify({
        "roll": roll,
        "win": win,
        "payout": payout
    })

# Stripe payment intent endpoint
@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    data = request.get_json()
    amount = int(data.get("amount", 0)) * 100  # Convert dollars to cents

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )
        return jsonify({"clientSecret": intent.client_secret})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Main entry point with Render-compatible port binding
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

