import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

from models import database, User
from configuration import Configuration
from utilities import hash_password, verify_password, is_valid_email

application = Flask(__name__)
application.config.from_object(Configuration)

# JWT Configuration
application.config["JWT_SECRET_KEY"] = "super-secret-key"
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour

jwt = JWTManager(application)
database.init_app(application)


@application.route("/register_customer", methods=["POST"])
def register_customer():
    return register_user("customer")


@application.route("/register_courier", methods=["POST"])
def register_courier():
    return register_user("courier")


def register_user(role):
    """Common registration logic for customers and couriers"""

    # Extract fields from request
    data = request.json if request.json else {}

    forename = data.get("forename", "")
    surname = data.get("surname", "")
    email = data.get("email", "")
    password = data.get("password", "")

    # Validate fields
    if not forename or len(forename) == 0:
        return jsonify(message="Field forename is missing."), 400

    if not surname or len(surname) == 0:
        return jsonify(message="Field surname is missing."), 400

    if not email or len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    if not password or len(password) == 0:
        return jsonify(message="Field password is missing."), 400

    # Validate email format
    if not is_valid_email(email):
        return jsonify(message="Invalid email."), 400

    # Validate password length
    if len(password) < 8:
        return jsonify(message="Invalid password."), 400

    #  Check for existing user
    existing_user = User.query.filter(User.email == email).first()
    if existing_user:
        return jsonify(message="Email already exists."), 400

    #  Create new user
    hashed_password = hash_password(password)

    new_user = User(
        email=email,
        password=hashed_password,
        forename=forename,
        surname=surname,
        role=role
    )

    #  Save to database
    database.session.add(new_user)
    database.session.commit()

    return "", 200


@application.route("/login", methods=["POST"])
def login():
    """User login endpoint"""

    #  Extract email and password
    data = request.json if request.json else {}

    email = data.get("email", "")
    password = data.get("password", "")

    #  Validate field presence
    if not email or len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    if not password or len(password) == 0:
        return jsonify(message="Field password is missing."), 400

    #  Validate email format
    if not is_valid_email(email):
        return jsonify(message="Invalid email."), 400

    #  Query user from database
    user = User.query.filter(User.email == email).first()

    # Verify password
    if not user or not verify_password(password, user.password):
        return jsonify(message="Invalid credentials."), 400

    # Create JWT with user information
    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": user.role
    }

    access_token = create_access_token(
        identity=user.email,
        additional_claims=additional_claims
    )

    # Step 7: Return access token
    return jsonify(accessToken=access_token), 200


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    """Delete user account"""

    # Extract user email from JWT
    email = get_jwt_identity()

    user = User.query.filter(User.email == email).first()

    if not user:
        return jsonify(message="Unknown user."), 400

    database.session.delete(user)
    database.session.commit()

    return "", 200


if __name__ == "__main__":
    PORT = os.environ.get("PORT", "5000")
    HOST = "0.0.0.0" if "PRODUCTION" in os.environ else "localhost"

    application.run(debug=True, port=PORT, host=HOST)