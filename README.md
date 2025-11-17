# Intercom API Integration with FastAPI

A production-ready FastAPI application for integrating with Intercom API to manage contacts and companies.

## 🚀 Features

- ✅ Create and retrieve Intercom contacts
- ✅ Create and retrieve Intercom companies
- ✅ API key authentication
- ✅ Automatic API documentation (Swagger UI & ReDoc)
- ✅ Request validation with Pydantic
- ✅ Async/await for better performance
- ✅ Comprehensive error handling
- ✅ CORS support

## 📋 Prerequisites

- Python 3.11 or higher
- Intercom account with API access token

## 🛠️ Installation

### Step 1: Install UV

UV is a blazingly fast Python package manager (10-100x faster than pip).

#### macOS and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Verify Installation

```bash
uv --version
```

You should see output like: `uv 0.x.x`

### Step 2: Clone/Create Project

```bash
# Create project directory
mkdir intercom-api
cd intercom-api

# Initialize UV project
uv init
```

### Step 3: Create Project Structure

```bash
# Create directory structure
mkdir -p app/{config,services,routes,middleware,models,utils}

# Create __init__.py files
touch app/__init__.py
touch app/config/__init__.py
touch app/services/__init__.py
touch app/routes/__init__.py
touch app/middleware/__init__.py
touch app/models/__init__.py
touch app/utils/__init__.py

# Create environment files
touch .env .env.example .gitignore
```

Your structure should look like:

```
intercom-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── intercom.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── contact.py
│   │   └── company.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── intercom_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── contact.py
│   │   └── company.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py
│   └── utils/
│       ├── __init__.py
│       └── responses.py
├── .env
├── .env.example
├── .gitignore
└── pyproject.toml
```

### Step 4: Install Dependencies

```bash
# Install all required packages
uv add fastapi uvicorn[standard] python-dotenv pydantic pydantic-settings python-intercom httpx python-multipart

# Install development dependencies (optional)
uv add --dev pytest pytest-asyncio black ruff
```

This will:

- Automatically create a virtual environment
- Install all dependencies
- Generate `pyproject.toml` and `uv.lock` files

### Step 5: Copy Code Files

Copy all the code from the "Complete FastAPI Intercom Code" artifact into their respective files:

- Copy each section marked with `# FILE: path/to/file.py` into the corresponding file

### Step 6: Configure Environment Variables

#### Get Your Intercom Access Token

1. Log in to your [Intercom account](https://app.intercom.com/)
2. Go to **Settings** → **Developers** → **Developer Hub**
3. Click **"New app"** or select an existing app
4. Go to the **"Authentication"** tab
5. Copy your **Access Token**

#### Create .env File

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Server Configuration
PORT=8000
ENVIRONMENT=development

# Intercom Configuration
INTERCOM_ACCESS_TOKEN=your_actual_intercom_token_here

# API Security
API_KEY=your_secure_api_key_here
```

**Important:**

- Replace `your_actual_intercom_token_here` with your real Intercom access token
- Replace `your_secure_api_key_here` with a secure random string (e.g., `sk_live_abc123xyz789`)

## 🏃 Running the Application

### Development Mode (with auto-reload)

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The server will start at: `http://localhost:8000`

### Production Mode

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Alternative: Create a Makefile

Create a `Makefile` in the project root:

```makefile
.PHONY: dev run test format lint install

install:
    uv sync

dev:
    uv run uvicorn app.main:app --reload --port 8000

run:
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test:
    uv run pytest

format:
    uv run black app/

lint:
    uv run ruff check app/
```

Then simply run:

```bash
make dev      # Start development server
make run      # Start production server
make test     # Run tests
make format   # Format code
```

## 📚 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints directly from the browser!

## 🧪 Testing the API

### Using cURL

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Create a Contact

```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_secure_api_key_here" \
  -d '{
    "email": "john.doe@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "custom_attributes": {
      "plan": "premium",
      "subscription_date": "2024-01-01"
    }
  }'
```

#### Get a Contact

```bash
curl -X GET http://localhost:8000/api/v1/contacts/{contact_id} \
  -H "x-api-key: your_secure_api_key_here"
```

#### Create a Company

```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_secure_api_key_here" \
  -d '{
    "company_id": "company_123",
    "name": "Acme Corporation",
    "website": "https://acme.com",
    "plan": "enterprise",
    "size": 50,
    "industry": "Technology"
  }'
```

#### Get a Company

```bash
curl -X GET http://localhost:8000/api/v1/companies/{company_id} \
  -H "x-api-key: your_secure_api_key_here"
```

### Using Python Requests

```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your_secure_api_key_here"

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# Create contact
contact_data = {
    "email": "jane.smith@example.com",
    "name": "Jane Smith",
    "phone": "+1987654321"
}

response = requests.post(
    f"{API_URL}/contacts",
    json=contact_data,
    headers=headers
)

print(response.json())
```

## 📋 Available Endpoints

| Method | Endpoint                 | Description      | Auth Required | Done? |
| ------ | ------------------------ | ---------------- | ------------- | ----- |
| GET    | `/`                      | Root endpoint    | ❌            | ❌    |
| GET    | `/health`                | Health check     | ❌            | ❌    |
| POST   | `/api/v1/contacts`       | Create a contact | ✅            | ❌    |
| GET    | `/api/v1/get-contacts`   | Get all contact  | ✅            | ❌    |
| GET    | `/api/v1/contacts/{id}`  | Get a contact    | ✅            | ❌    |
| POST   | `/api/v1/companies`      | Create a company | ✅            | ❌    |
| GET    | `/api/v1/companies/{id}` | Get a company    | ✅            | ❌    |

## 🔑 Authentication

All API endpoints (except root and health check) require an API key passed in the header:

```
x-api-key: your_secure_api_key_here
```

## 📦 UV Commands Reference

```bash
# Add a package
uv add package-name

# Add a development package
uv add --dev package-name

# Remove a package
uv remove package-name

# Sync dependencies from lock file
uv sync

# Update all packages
uv lock --upgrade

# Run a command
uv run python script.py

# Run the app
uv run uvicorn app.main:app --reload
```

## 🐛 Troubleshooting

### Issue: "uv: command not found"

**Solution:** Restart your terminal after installing UV, or manually add UV to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"
```

### Issue: "ModuleNotFoundError"

**Solution:** Make sure all dependencies are installed:

```bash
uv sync
```

### Issue: "Intercom API Error: Unauthorized"

**Solution:** Check that your `INTERCOM_ACCESS_TOKEN` in `.env` is correct and has the necessary permissions.

### Issue: "Invalid API key"

**Solution:** Ensure you're passing the correct API key in the `x-api-key` header that matches your `.env` file.

### Issue: Port already in use

**Solution:** Change the port in your `.env` file or specify a different port:

```bash
uv run uvicorn app.main:app --reload --port 8001
```

## 🚀 Deployment

### Deploy to Production

For production deployment, consider:

1. Set `ENVIRONMENT=production` in `.env`
2. Use a production-grade server with multiple workers
3. Set up reverse proxy (Nginx)
4. Use environment variables from your hosting platform
5. Enable HTTPS

Example production command:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t intercom-api .
docker run -p 8000:8000 --env-file .env intercom-api
```

## 🧪 Running Tests (Optional)

If you installed dev dependencies:

```bash
uv run pytest
```

---

Made with ❤️ using FastAPI and UV
