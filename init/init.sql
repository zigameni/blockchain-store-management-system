DROP DATABASE IF EXISTS store_database;
CREATE DATABASE store_database;
USE store_database;

-- USERS table, for Customer, Courier, Owner
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(256) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    forename VARCHAR(256) NOT NULL,
    surname VARCHAR(256) NOT NULL ,
    role ENUM('customer', 'courier', 'owner') NOT NULL
);

-- PRODUCTS table
CREATE TABLE products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(256) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL
);

-- CATEGORIES table
CREATE TABLE categories (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(256) NOT NULL UNIQUE
);

-- Many-to-many relationships between: products and categories
CREATE TABLE product_categories (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_category (product_id, category_id)
);

CREATE TABLE orders (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status ENUM('CREATED', 'PENDING', 'COMPLETE') NOT NULL DEFAULT 'CREATED',
    timestamp DATETIME NOT NULL,
    contract_address varchar(64) DEFAULT NULL,
    customer_address varchar(64) DEFAULT NULL,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Many-to-many relationship: orders and products
CREATE TABLE order_products (
    id INT NOT NULL  AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES  orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES  products(id) ON DELETE  CASCADE
);

-- The owner account
-- Password hash for 'evenmoremoney'
INSERT INTO users (email, password, forename, surname, role) VALUES (
                                                                     'onlymoney@gmail.com',
                                                                     '$2b$12$wZcbhs75LSsHp3asVGv0veSXZecNx4FXjdPxfC7TC1ZNlu8BvB4dC',
                                                                     'Scrooge',
                                                                     'McDuck',
                                                                     'owner'
                                                                    );
