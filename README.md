# ABAN Tether Exchange API

This project is an implementation task for ABAN Tether. The goal is to design an API for registering purchase orders from an exchange or cryptocurrency exchange under specific conditions.

## Features

- **User Management**: Create and authenticate users.
- **Currency Management**: List available currencies.
- **Transaction Management**: Submit transactions and manage their states.
- **Event Handling**: Settle transactions with exchange events.
- **Scheduled Tasks**: Periodically revert stuck transactions to the submitted state.

## Technology Stack

- **Python**: The main programming language.
- **Nameko**: A microservices framework for Python.
- **SQLAlchemy**: An ORM for interacting with the database.
- **Marshmallow**: For schema validation and serialization/deserialization.
- **Alembic**: For database migrations.
- **Docker**: For containerization.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose

### Local Development Setup

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/amir-mhp/aban-tether-task.git
   cd aban-tether-exchange

2. **Build the Docker Image**:
   ```sh
   docker build -t abantether/core .

3. **Start the Services**:
   ```sh
   docker-compose up -d

4. **Run Database Migrations**:
   ```sh
   docker-compose run --rm core alembic upgrade head
   
5. **Add Default Currencies:**:
   ```sh
   docker-compose run --rm core python pre_deploy/add_default_currency.py

6. **Access the Application**:

   The application will be running at http://localhost:8005