import json
import os

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity

from configuration import Configuration
from models import database, Order, User
from utilities import get_web3, read_file, is_valid_address, get_owner_account, send_transaction

application = Flask(__name__)
application.config.from_object(Configuration)

# # JWT Configuration
# application.config["JWT_SECRET_KEY"] = "JWT_SECRET_DEV_KEY"
# application.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt = JWTManager(application)
database.init_app(application)

@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
def orders_to_deliver():
    """Get all orders that haven't been picked up yet"""
    claims = get_jwt()
    if claims.get("roles") != "courier":
        return jsonify(msg="Missing Authorization Header"), 401

    orders = Order.query.filter(
        Order.status == "CREATED"
    ).order_by(Order.id.asc()).all()

    orders_list = []
    for order in orders:
        customer = User.query.filter(User.id == order.customer_id).first()
        if customer:
            order_dict = {
                "id": order.id,
                "email": customer.email
            }
            orders_list.append(order_dict)

    return jsonify(orders=orders_list), 200

    # -- START MODIFICATION --
    # orders = Order.query.filter(
    #     Order.status == "CREATED",
    #     Order.contract_address.isnot(None)  # Only query orders with contracts
    # ).order_by(Order.id.asc()).all()
    #
    # orders_list = []
    # web3 = get_web3()
    # abi = json.loads(read_file("./blockchain/output/OrderPayment.abi"))
    #
    # for order in orders:
    #     try:
    #         contract = web3.eth.contract(address=order.contract_address, abi=abi)
    #         is_paid = contract.functions.isPaid().call()
    #
    #         # Only include the order if it has been paid
    #         if not is_paid:
    #             continue
    #     except Exception as e:
    #         print(f"Error checking payment for order {order.id}: {str(e)}")
    #         continue
    #
    #     customer = User.query.filter(User.id == order.customer_id).first()
    #     if customer:
    #         orders_list.append({
    #             "id": order.id,
    #             "email": customer.email
    #         })
    #
    # return jsonify(orders=orders_list), 200


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
def pick_up_order():
    """Pick up an order for delivery and bind courier to smart contract"""
    claims = get_jwt()
    if claims.get("roles") != "courier":
        return jsonify(msg="Missing Authorization Header"), 401

    courier_email = get_jwt_identity()
    data = request.json if request.json else {}

    if "id" not in data:
        return jsonify(message="Missing order id."), 400

    order_id = data["id"]
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify(message="Invalid order id."), 400

    order = Order.query.filter(Order.id == order_id).first()

    # 1. Check order validity and status FIRST
    if not order or order.status != "CREATED":
        return jsonify(message="Invalid order id."), 400

    # 2. Check for contract address
    if not order.contract_address:
        return jsonify(message="Invalid order id."), 400

    # 3. NOW, validate the courier's address
    if "address" not in data:
        return jsonify(message="Missing address."), 400

    courier_address = data["address"]
    if not courier_address or courier_address == '':
        return jsonify(message="Missing address."), 400

    if not is_valid_address(courier_address):
        return jsonify(message="Invalid address."), 400

    web3 = get_web3()
    courier_address = web3.to_checksum_address(courier_address)

    # Verify payment has been made via smart contract
    try:
        abi = json.loads(read_file("./blockchain/output/OrderPayment.abi"))
        contract = web3.eth.contract(address=order.contract_address, abi=abi)

        is_paid = contract.functions.isPaid().call()
        if not is_paid:
            return jsonify(message="Transfer not complete."), 400

        # Assign courier to contract (owner pays for this transaction)
        owner_address, owner_private_key = get_owner_account()

        assign_txn = contract.functions.assignCourier(
            courier_address
        ).build_transaction({
            'from': owner_address,
            'nonce': web3.eth.get_transaction_count(owner_address),
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })

        # Send transaction
        receipt = send_transaction(assign_txn, owner_private_key)

        # Update order status
        order.status = "PENDING"
        database.session.commit()

        return "", 200

    except Exception as e:
        database.session.rollback()
        return jsonify(message=f"Error assigning courier: {str(e)}"), 400


if __name__ == "__main__":
    PORT = os.environ.get("PORT", "5000")
    HOST = "0.0.0.0" if "PRODUCTION" in os.environ else "localhost"

    application.run(debug=True, port=PORT, host=HOST)