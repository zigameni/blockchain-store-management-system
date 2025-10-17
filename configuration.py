import os

# Define constants
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "root")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "root")
DATABASE_URL = os.environ.get("DATABASE_URL", "localhost")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "store_database")
BLOCKCHAIN_URL = os.environ.get("BLOCKCHAIN_URL", "http://127.0.0.1:8545")

class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URL}/{DATABASE_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
