<<<<<<< HEAD
# Maweshi Muhafiz
=======
# Maweshi Muhafiz — Backend

AI-powered livestock assistance system backend.

## Purpose

REST API backend for Maweshi Muhafiz. Handles livestock health assessment, animal records, and AI-assisted veterinary guidance. Built with Flask using the Application Factory pattern for clean scalability.

## Technology

- **Language:** Python 3.10+
- **Framework:** Flask 3
- **Architecture:** REST API, Application Factory, Blueprints
- **Database:** TBD (not yet configured)

## Project Structure

```
backend(Maweshi Muhafiz)/
├── app/
│   ├── __init__.py       # Application factory (create_app)
│   ├── config.py         # Environment-based configuration
│   ├── models/           # Database models (added when DB is chosen)
│   ├── routes/           # Flask Blueprints — one file per feature
│   ├── services/         # Business logic, decoupled from routes
│   └── utils/            # Shared helpers (formatters, validators)
├── tests/                # pytest test suite
├── .env.example          # Environment variable template
├── .gitignore
├── requirements.txt
├── run.py                # App entry point
└── README.md
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

**Windows (Git Bash / PowerShell):**
```bash
source venv/Scripts/activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set `SECRET_KEY` and any other required values.

## Running the Server

```bash
python run.py
```

The server starts at `http://127.0.0.1:5000` in development mode.

## Running Tests

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

## Health Endpoint

```
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "message": "Pashu Rakhwala backend is running"
}
```

Used to verify the backend is up and reachable.
>>>>>>> Implement Feature 1: Digital Animal Profile Management with MongoDB Atlas
