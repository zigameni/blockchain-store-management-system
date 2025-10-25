import os

# Define constants
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "root")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "root")
DATABASE_URL = os.environ.get("DATABASE_URL", "localhost")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "store_database")
BLOCKCHAIN_URL = os.environ.get("BLOCKCHAIN_URL", "http://127.0.0.1:8545")

# JWT Configuration - MUST be the same across all services
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "JWT_SECRET_DEV_KEY")
class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URL}/{DATABASE_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour