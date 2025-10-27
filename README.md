# Store Management System with Blockchain Payments

A containerized multi-user store management system built with Flask, SQLAlchemy, and Ethereum smart contracts.

## Features

- **User Management**: Authentication for customers, couriers, and store owners
- **Product Management**: CSV upload, search, and statistics
- **Order Processing**: Full order lifecycle with status tracking
- **Blockchain Payments**: Ethereum smart contracts for secure payment escrow
- **Docker Deployment**: Complete containerized system with Docker Compose

## Quick Start

```bash
# Clone and start
git clone <your-repo-url>
cd store-management-system
docker-compose up --build
```

**Services:**
- Authentication: `http://localhost:5001`
- Owner: `http://localhost:5002`
- Customer: `http://localhost:5003`
- Courier: `http://localhost:5004`
- Blockchain: `http://localhost:8545`

## Default Owner Account

```
Email: onlymoney@gmail.com
Password: evenmoremoney
```

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: MySQL
- **Blockchain**: Solidity, Web3.py, Ganache
- **Deployment**: Docker, Docker Compose

## Project Structure

```
.
├── authentication/       # Auth service
├── owner/               # Owner service
├── customer/            # Customer service
├── courier/             # Courier service
├── blockchain/          # Smart contracts
├── models.py           # Database models
├── configuration.py    # Config
└── docker-compose.yml  # Orchestration
```

## API Documentation

### Authentication
- `POST /register_customer` - Register customer
- `POST /register_courier` - Register courier
- `POST /login` - User login

### Owner
- `POST /update` - Upload products (CSV)
- `GET /product_statistics` - Product stats
- `GET /category_statistics` - Category stats

### Customer
- `GET /search` - Search products
- `POST /order` - Create order
- `POST /generate_invoice` - Get payment invoice
- `GET /status` - View orders
- `POST /delivered` - Confirm delivery

### Courier
- `GET /orders_to_deliver` - Available orders
- `POST /pick_up_order` - Pick up order

## Testing

```bash
cd tests
python main.py
```

## License

Academic project - See LICENSE file

## Tags

`flask` `docker` `blockchain` `ethereum` `smart-contracts` `sqlalchemy` `web3py` `microservices` `rest-api` `jwt` `python` `mysql` `e-commerce` `order-management` `payment-system`
