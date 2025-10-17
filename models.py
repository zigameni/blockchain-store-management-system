from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

db = SQLAlchemy()

# -- USERS table, for Customer, Courier, Owner
# CREATE TABLE users (
#     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#     email VARCHAR(256) NOT NULL UNIQUE,
#     password VARCHAR(256) NOT NULL,
#     forename VARCHAR(256) NOT NULL,
#     surname VARCHAR(256) NOT NULL ,
#     role ENUM('customer', 'courier', 'owner') NOT NULL
# );
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    forename = db.Column(db.String(256), nullable=False)
    surname = db.Column(db.String(256), nullable=False)
    role = db.COlumn(db.Enum('customer', 'courier', 'owner'), nullable=False)

    # Relationship
    orders = db.relationship('Order', back_populates='customer', lazy=True)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

# -- PRODUCTS table
# CREATE TABLE products (
#     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(256) NOT NULL UNIQUE,
#     price DECIMAL(10, 2) NOT NULL
# );
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    categories = db.relationship("Category", secondary="product_categories", back_populates="products")
    order_products = db.relationship("OrderProduct", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name} - {self.price}>"



# -- CATEGORIES table
# CREATE TABLE categories (
#     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(256) NOT NULL UNIQUE
# );
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)

    # Relationships
    products = db.relationship("Product", secondary="product_categories", back_populates="categories")

    def __repr__(self):
        return f"<Category {self.name}>"


# -- Many-to-many relationships between: products and categories
# CREATE TABLE product_categories (
#     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#     product_id INT NOT NULL,
#     category_id INT NOT NULL,
#     FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
#     FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
#     UNIQUE KEY unique_product_category (product_id, category_id)
# );
#

class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)


# CREATE TABLE orders (
#     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#     customer_id INT NOT NULL,
#     price DECIMAL(10, 2) NOT NULL,
#     status ENUM('CREATED', 'PENDING', 'COMPLETE') NOT NULL DEFAULT 'CREATED',
#     timestamp DATETIME NOT NULL,
#     contract_address varchar(64) DEFAULT NULL,
#     customer_address varchar(64) DEFAULT NULL,
#     FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
# );

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('CREATED', 'PENDING', 'COMPLETE'), nullable=False, default='CREATED')
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    contract_address = db.Column(db.String(64), nullable=True)
    customer_address = db.Column(db.String(64), nullable=True)

    # Relationships
    customer = db.relationship("User", back_populates="orders")
    order_products = db.relationship("OrderProduct", back_populates="order")

    def __repr__(self):
        return f"<Order {self.id} - {self.status} - ${self.price}>"



# -- Many-to-many relationship: orders and products
# CREATE TABLE order_products (
#     id INT NOT NULL  AUTO_INCREMENT PRIMARY KEY,
#     order_id INT NOT NULL,
#     product_id INT NOT NULL,
#     quantity INT NOT NULL,
#     FOREIGN KEY (order_id) REFERENCES  orders(id) ON DELETE CASCADE,
#     FOREIGN KEY (product_id) REFERENCES  products(id) ON DELETE  CASCADE
# );

class OrderProduct(db.Model):
    __tablename__ = "order_products"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Relationships
    order = db.relationship("Order", back_populates="order_products")
    product = db.relationship("Product", back_populates="order_products")

    def __repr__(self):
        return f"<OrderProduct order={self.order_id} product={self.product_id} qty={self.quantity}>"

