# OHTUIE Backend

OHTUIE is a robust backend API built with **FastAPI**, designed to manage menstrual cycle tracking, daily logs, and user data. It features a scalable architecture with PostgreSQL as the primary database.

## 🚀 Features

- **User Management**: Secure authentication with JWT and password hashing (bcrypt).
- **Cycle Tracking**: Record and manage menstrual cycle data.
- **Daily Logs**: Track symptoms, moods, and flow on a daily basis.
- **Audit Logging**: Track system events and security-related actions.
- **Admin Dashboard Ready**: Includes roles and specialized endpoints for management.
- **Environment Driven**: Easily configurable via environment variables.

## 🛠️ Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (with `asyncpg`)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Security**: [Jose](https://python-jose.readthedocs.io/en/latest/) (JWT), [Passlib](https://passlib.readthedocs.io/) (bcrypt)

## 📂 Project Structure

```text
OHTUIE/
├── app/
│   ├── api/            # API v1 routes and endpoints
│   ├── core/           # Configuration, security, and global settings
│   ├── crud/           # CRUD (Create, Read, Update, Delete) operations
│   ├── db/             # Database session and base configuration
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic schemas for request/response validation
│   ├── services/       # Auxiliary business logic services
│   └── main.py         # Application entry point
├── init_db.sql         # Database initialization script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # Project documentation
```

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd OHTUIE
```

### 2. Set up a virtual environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Copy the `.env.example` file to `.env` and fill in your details:
```bash
cp .env.example .env
```
> [!IMPORTANT]
> Make sure to update the `DATABASE_URL` and `SECRET_KEY` in your `.env` file before running the application.

### 5. Database Initialization
Use the provided `init_db.sql` script to set up your PostgreSQL database schema.

### 6. Run the application
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at `http://127.0.0.1:8000/docs`.

## ☁️ Deployment on Railway

This project is configured to be deployed on **Railway**.

### 1. Requirements
Ensure you have the following environment variables configured in the Railway dashboard:
- `DATABASE_URL`: Your PostgreSQL connection string.
- `SECRET_KEY`: A secure random string for JWT.
- `PROJECT_NAME`: (Optional) The name of your project.
- `PORT`: (Managed by Railway) The port the app will listen on.

### 2. Automatic Configuration
The project includes a `Procfile` that Railway uses to start the application with the correct host and port:
```text
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 3. Verification
Once deployed, you can verify the application status at `https://<your-project-url>.up.railway.app/`.

## 🔒 Security Note: .env Files

If your `.env` file was already tracked by Git before being added to `.gitignore`, it will continue to be uploaded. To stop tracking it without deleting it locally, run:

```bash
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking .env file"
git push
```

## 📄 License

This project is licensed under the MIT License.
