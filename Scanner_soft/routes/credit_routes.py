from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User

credit_blueprint = Blueprint('credit', __name__, url_prefix='/api/credits')

#   Get user's credit balance
@credit_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_credits():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"credits": user.credits}), 200

#  Deduct credits when scanning a document
@credit_blueprint.route('/deduct', methods=['POST'])
@jwt_required()
def deduct_credits():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.deduct_credits(1):  # imporatant credit diduction logic here
        return jsonify({"message": "Scan successful, 1 credit deducted", "remaining_credits": user.credits}), 200

    return jsonify({"error": "Insufficient credits"}), 400

#  Admin adds credits to a user
@credit_blueprint.route('/add', methods=['POST'])
@jwt_required()
def add_credits():
    data = request.get_json()
    user_id = data.get("user_id")  # Admin provides user ID
    amount = data.get("amount")

    if not user_id or not amount:
        return jsonify({"error": "Missing user_id or amount"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.add_credits(amount)
    return jsonify({"message": f"Added {amount} credits to user {user_id}", "new_balance": user.credits}), 200
