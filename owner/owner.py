import os

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

from configuration import Configuration
from models import database, Product, Category, ProductCategory

application = Flask(__name__)
application.config.from_object(Configuration)

# Jwt configuration
# application.config["JWT_SECRET_KEY"] = "JWT_SECRET_DEV_KEY"
# application.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt = JWTManager(application)
database.init_app(application)

@application.route("/update", methods=["POST"])
@jwt_required()
def update():
    """Add products via CSV file"""

    # only owner can use this functionality
    claims = get_jwt()
    if claims.get("roles") != "owner":
        return jsonify(msg="Missing Authorization Header"), 401

    # Get file from request
    if "file" not in request.files:
        return jsonify(message="Field file is missing."), 400

    file = request.files["file"]
    # read file
    try:
        content = file.stream.read().decode("utf-8")
    except Exception as e:
        return jsonify(message="Error reading file."), 400

    lines = content.strip().split("\n")

    # Validate lines
    products_to_add = []

    for line_number, line in enumerate(lines):
        parts = line.split(",")

        # check number of fields
        if len(parts) != 3:
            return jsonify(message=f"Incorrect number of values on line {line_number}."), 400

        categories_str = parts[0].strip();
        product_name = parts[1].strip();
        price_str = parts[2].strip();

        # Price check
        try:
            price = float(price_str)
            if price <= 0:
                return jsonify(message=f"Incorrect price on line {line_number}."), 400
        except ValueError:
            return jsonify(message=f"Incorrect price on line {line_number}."), 400

        # check if product exists
        existing_product = Product.query.filter(Product.name==product_name).first()
        if existing_product:
            return jsonify(message=f"Product {product_name} already exists."), 400

        # parse categories
        category_names = [cat.strip() for cat in categories_str.split("|")]

        products_to_add.append({
            "name": product_name,
            "price": price,
            "categories": category_names
        })

    # Create products for database
    try:
        for product_data in products_to_add:
            new_product = Product(
                name=product_data["name"],
                price=product_data["price"]
            )
            database.session.add(new_product)
            database.session.flush() # get id without commiting

            for category_name in product_data["categories"]:
                # check if it exists
                category = Category.query.filter(Category.name==category_name).first()

                if not category:
                    # create new category
                    category = Category(name=category_name)
                    database.session.add(category)
                    database.session.flush()

                # create relationship product-category
                product_category = ProductCategory(
                    product_id=new_product.id,
                    category_id=category.id
                )
                database.session.add(product_category)

        # Commit all changes
        database.session.commit()

    except Exception as e:
        database.session.rollback() # Dont save any changes
        return jsonify(message=f"Database error: {str(e)}"), 400

    return "", 200


@application.route("/product_statistics", methods=["GET"])
@jwt_required()
def product_statistics():
    """Get statistics for all products with at least one sale"""

    #verify user is owner
    claims = get_jwt()
    if claims.get("roles") != "owner":
        return jsonify(msg="Missing Authorization Header"), 401

    # Get sold and waiting queantities
    from sqlalchemy import func
    from models import OrderProduct, Order

    # Get sold quantities (Complete orders)
    sold_query = database.session.query(
        Product.name,
        func.sum(OrderProduct.quantity).label("sold")
    ).join(
        OrderProduct, Product.id == OrderProduct.product_id
    ).join(
        Order, OrderProduct.order_id == Order.id
    ).filter(
        Order.status == "COMPLETE"
    ).group_by(
        Product.id, Product.name
    )

    # Get waiting quantities, Created and Pending orders
    wating_query = database.session.query(
        Product.name,
        func.sum(OrderProduct.quantity).label("waiting")
    ).join(
        OrderProduct, Product.id == OrderProduct.product_id
    ).join(
        Order, OrderProduct.order_id == Order.id
    ).filter(
        Order.status.in_(["CREATED", "PENDING"])
    ).group_by(
        Product.id, Product.name
    )

    # dicts for easy lookup
    sold_dict = {name: int(sold) for name, sold in sold_query.all()}
    waiting_dict = {name: int(waiting) for name, waiting in wating_query.all()}

    # Get all product that have atleast one sale
    all_products_name = set(sold_dict.keys()) | set(waiting_dict.keys())

    # build stats list
    statistics = []
    for name in all_products_name:
        statistics.append({
            "name": name,
            "sold": sold_dict.get(name, 0),
            "waiting": waiting_dict.get(name, 0)
        })

    return jsonify(statistics=statistics), 200

@application.route("/category_statistics", methods=["GET"])
@jwt_required()
def category_statistics():
    """Get categories sorted by delivered product count"""

    # verify user is owner
    claims = get_jwt()
    if claims.get("roles") != "owner":
        return jsonify(msg="Missing Authorization Header"), 401

    from sqlalchemy import func
    from models import OrderProduct, Order

    # query to count delivered products per category
    category_stats = database.session.query(
        Category.name,
        func.sum(OrderProduct.quantity).label("delivered_count")
    ).join(
        ProductCategory, Category.id == ProductCategory.category_id
    ).join(
        Product,ProductCategory.product_id == Product.id
    ).join(
        OrderProduct, Product.id == OrderProduct.product_id
    ).join(
        Order, OrderProduct.order_id == Order.id
    ).filter(
        Order.status == "COMPLETE"
    ).group_by(
        Category.id, Category.name
    ).order_by(
        func.sum(OrderProduct.quantity).desc(),
        Category.name.asc()
    ).all()

    # Extract category names
    statistics = [name for name, count in category_stats]

    return jsonify(statistics=statistics), 200


if __name__ == "__main__":
    PORT = os.environ.get("PORT", "5000")
    HOST = "0.0.0.0" if "PRODUCTION" in os.environ else "localhost"

    application.run(debug=True, host=HOST, port=PORT)