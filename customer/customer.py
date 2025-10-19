import datetime
import os

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity


from configuration import Configuration
from models import database, Product, Category, User, Order, OrderProduct

application= Flask(__name__)
application.config.from_object(Configuration)

# Jwt configuration
application.config["JWT_SECRET_KEY"] = "super-secret-key"
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt = JWTManager(application)
database.init_app(application)

@application.route("/search", methods=["GET"])
@jwt_required()
def search():
    """Search for products by name and/or category"""

    # Verify user
    claims = get_jwt()
    if claims.get("roles") != "customer":
        return jsonify(msg="Missing Authorization Header"), 401

    # Get query parameters
    name_filter = request.args.get("name", "");
    category_filter = request.args.get("category", "");

    # start with base query
    products_query = Product.query
    categories_query = Category.query

    # apply filters if provided
    if name_filter:
        products_query = products_query.filter(Product.name.like(f"%{name_filter}%"))

    if category_filter:
        # filter products that belong to categories matching the filter.
        products_query = products_query.join(
            Product.categories
        ).filter(
            Category.name.like(f"%{category_filter}%")
        )

        # filter categories by name
        categories_query = categories_query.filter(
            Category.name.like(f"%{category_filter}%")
        )

    # if name filter is applied only show categories of matching products
    if name_filter:
        categories_query = categories_query.join(
            Category.products
        ).filter(
            Product.name.like(f"%{name_filter}%")
        )

    # Get unique categories
    categories = categories_query.distinct().all()
    category_names = [cat.name for cat in categories]

    # Get products with all their categories
    products = products_query.distinct().all()

    products_list = []

    for product in products:
        product_dict = {
            "categories": [cat.name for cat in product.categories],
            "id": product.id,
            "name": product.name,
            "price": float(product.price)
        }
        products_list.append(product_dict)

    return jsonify(categories=category_names, products=products_list), 200

@application.route("/order", methods=["POST"])
@jwt_required()
def create_order():
    """Create a new order"""
    # Verify user
    claims = get_jwt()
    if claims.get("roles") != "customer":
        return jsonify(msg="Missing Authorization Header"), 401

    # Customer email
    customer_email = get_jwt_identity();

    # Request data:
    data = request.json if request.json else {}

    if "requests" not in data:
        return jsonify(message="Field requests is missing."), 400

    requests_list = data["requests"]

    if not isinstance(requests_list, list):
        return jsonify(message="Field requests is missing."), 400

    # validate each request
    validated_items = []

    for index, item in enumerate(requests_list):
        # validate id
        if "id" not in item:
            return jsonify(message=f"Product id is missing for request number {index}."), 400

        # Validate quantity
        if "quantity" not in item:
            return jsonify(message=f"Product quantity is missing for request number {index}."), 400

        product_id = item["id"]
        product_quantity = item["quantity"]

        # Validate id is a positive integer
        if not isinstance(product_id, int) or product_id <= 0:
            return jsonify(message=f"Invalid product id for request number {index}."), 400

        # Validate quantity is a positive integer
        if not isinstance(product_quantity, int) or product_quantity <= 0:
            return jsonify(message=f"Invalid product quantity for request number {index}."), 400

        # Check if product exists
        product = Product.query.filter(Product.id == product_id).first();
        if not product:
            return jsonify(message=f"Invalid product for request number {index}."), 400

        validated_items.append({
            "product": product,
            "quantity": product_quantity
        })

    # calculate total price
    total_price = sum(item["product"].price * item["quantity"] for item in validated_items)

    # Get customer
    customer = User.query.filter(User.email == customer_email).first()

    new_order = Order(
        customer_id=customer.id,
        price=total_price,
        status="CREATED",
        timestamp=datetime.datetime.utcnow()
    )

    database.session.add(new_order)
    database.session.flush()  # Get order ID

    # Create order products
    for item in validated_items:
        order_product = OrderProduct(
            order_id=new_order.id,
            product_id=item["product"].id,
            quantity=item["quantity"]
        )
        database.session.add(order_product)

    # Save transation
    database.session.commit()

    # return order id
    return jsonify(id=new_order.id), 200




@application.route("/status", methods=["GET"])
@jwt_required()
def status():
    """Get all orders for authenticated customers"""

    claims = get_jwt()
    if claims.get("roles") != "customer":
        return jsonify(msg="Missing Authorization Header"), 401

    customer_email = get_jwt_identity()

    customer = User.query.filter(User.email == customer_email).first()

    # Get all orders for this customer
    orders = Order.query.filter(
        Order.customer_id == customer.id
    ).order_by(Order.timestamp.asc()).all()

    # build response
    orders_list = []

    for order in orders:
        products_list = []

        for order_product in order.order_products:
            product = order_product.product

            product_dict = {
                "categories": [cat.name for cat in product.categories],
                "name": product.name,
                "price": float(product.price),
                "quantity": order_product.quantity
            }

            products_list.append(product_dict)

        # Timestamp format
        timestamp_str = order.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        order_dict = {
            "products": products_list,
            "price": float(order.price),
            "status": order.status,
            "timestamp": timestamp_str
        }
        orders_list.append(order_dict)

    return jsonify(orders=orders_list), 200



@application.route("/delivered", methods=["POST"])
@jwt_required()
def confirm_delivery():
    """Confirm that order has been delivered"""

    claims = get_jwt()
    if claims.get("roles") != "customer":
        return jsonify(msg="Missing Authorization Header"), 401

    # Get request data
    data = request.json if request.json else {}

    # Step 1: Validate order id presence
    if "id" not in data:
        return jsonify(message="Missing order id."), 400

    order_id = data["id"]

    # Step 2: Validate order id format
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify(message="Invalid order id."), 400

    # Step 3: Fetch order
    order = Order.query.filter(Order.id == order_id).first()

    # Step 4: Validate order exists
    if not order:
        return jsonify(message="Invalid order id."), 400

    if order.status == "CREATED":
        return jsonify(message="Delivery not complete."), 400

    # Step 5: Validate order status is PENDING
    if order.status != "PENDING":
        return jsonify(message="Invalid order id."), 400

        # Step 5: Validate order status is PENDING

    # Step 6: Update status to COMPLETE
    order.status = "COMPLETE"

    # Step 7: Commit changes
    database.session.commit()

    return "", 200

if __name__ == "__main__":
    PORT = os.environ.get("PORT", "5000")
    HOST = "0.0.0.0" if "PRODUCTION" in os.environ else "localhost"

    application.run(debug=True, host=HOST, port=PORT)
