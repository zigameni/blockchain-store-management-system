import os

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity

from configuration import Configuration
from models import database, Order, User

application = Flask(__name__)
application.config.from_object(Configuration)

# JWT Configuration
application.config["JWT_SECRET_KEY"] = "super-secret-key"
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt = JWTManager(application)
database.init_app(application)

@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
def orders_to_deliver():
    """Get all orders that haven't been picked up yet"""

    # Verify user is courier
    claims = get_jwt()
    if claims.get("roles") != "courier":
        return jsonify(msg="Missing Authorization Header"), 401

    # Query orders with CREATED status
    orders = Order.query.filter(
        Order.status == "CREATED"
    ).order_by(Order.id.asc()).all()

    # Build response
    orders_list = []

    for order in orders:
        customer = User.query.filter(User.id == order.customer_id).first()

        order_dict = {
            "id": order.id,
            "email": customer.email
        }
        orders_list.append(order_dict)

    return jsonify(orders=orders_list), 200


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
def pick_up_order():
    """Pick up an order for delivery"""

    # Verify user is courier
    claims = get_jwt()
    if claims.get("roles") != "courier":
        return jsonify(msg="Missing Authorization Header"), 401

    # Get courier email from JWT
    courier_email = get_jwt_identity()

    # Get request data
    data = request.json if request.json else {}

    # Step 1: Validate order id presence
    if "id" not in data:
        return jsonify(message="Missing order id."), 400

    order_id = data["id"]

    # Step 2: Validate order id format
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify(message="Invalid order id."), 400

    # Step 3: Fetch order from database
    order = Order.query.filter(Order.id == order_id).first()

    # Step 4: Validate order exists and status is CREATED
    if not order:
        return jsonify(message="Invalid order id."), 400

    if order.status != "CREATED":
        return jsonify(message="Invalid order id."), 400

    # Step 5: Update order status to PENDING
    order.status = "PENDING"

    # Step 6: Associate courier with order (we'll add this field later for blockchain)
    # For now, just update the status

    # Step 7: Commit changes
    database.session.commit()

    return "", 200


if __name__ == "__main__":
    PORT = os.environ.get("PORT", "5000")
    HOST = "0.0.0.0" if "PRODUCTION" in os.environ else "localhost"

    application.run(debug=True, port=PORT, host=HOST)