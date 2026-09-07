# Pharmacy Management API (Backend)

A robust RESTful API designed to manage multi-branch pharmacy operations. Built with **FastAPI** and **PostgreSQL**, this backend handles everything from point-of-sale (POS) transactions and inventory tracking to employee attendance and role-based access control.

> **Note:** This repository currently contains only the backend API services. The frontend application is in development.

## Features

* **Multi-Branch Isolation:** Manages data across multiple pharmacy locations, ensuring cashiers only access inventory and sales for their assigned branch.
* **Atomic POS Transactions:** Uses strict database transactional locks to prevent race conditions during concurrent sales, guaranteeing accurate inventory counts.
* **Role-Based Access Control (RBAC):** Differentiates permissions between `ADMIN` (global management, purchasing) and `CAJERO` (sales, attendance).
* **Inventory Management:** Tracks product stock, expiration dates, and low-stock alerts.
* **Stateless Authentication:** Secured via JSON Web Tokens (JWT) and Argon2 password hashing.
* **Employee Attendance:** Built-in time-clock functionality for staff check-ins and check-outs.

## Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
* **Database:** [PostgreSQL](https://www.postgresql.org/)
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) & [SQLModel](https://sqlmodel.tiangolo.com/)
* **Authentication:** PyJWT, Passlib (Argon2)
* **Server:** Uvicorn (ASGI)

## Prerequisites

Before running this project, ensure you have the following installed:
* Python 3.10 or higher
* PostgreSQL running locally or remotely

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SebastianHdzDev/Pharmacy-Management-API.git
   cd Pharmacy-Management-API
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and configure your database connection and JWT secrets:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/farmacia_db
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
   *(Be sure to replace the `DATABASE_URL` credentials with your actual PostgreSQL setup).*

5. **Initialize the Database:**
   Ensure your database is running, then you can create the first admin user (which may also initialize the tables depending on your setup):
   ```bash
   python crear_admin.py
   ```

## Start the Server

You can start the development server using the provided run script or via Uvicorn:

```bash
python run.py
# OR
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can explore and test the endpoints directly from your browser:

* **Swagger UI (Interactive):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc (Alternative):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

You can use the Swagger UI to create test data, log in to receive a JWT token, and test the protected endpoints without needing a frontend client.

## Future Roadmap (Frontend Integration)

* Implementation of a modern React/Next.js frontend.
* Advanced daily cash register (Corte de Caja) reporting.
