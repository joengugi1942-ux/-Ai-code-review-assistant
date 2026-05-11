# 🤖 Meet Lapo
Lapo is a FastAPI-powered AI Code Review Assistant designed to be your team's digital senior developer. By integrating directly with GitHub, Lapo analyzes pull requests in real-time to ensure your code is performant, secure, and idiomatic.

"Lapo doesn't just catch bugs; it helps you become a better coder."

## Features

- **AI Code Review**: Analyze code for style, correctness, and performance using Groq LLM
- **Security Scanning**: Detect secrets, unsafe patterns, and security vulnerabilities
- **GitHub Integration**: Analyze repositories and pull requests via GitHub API
- **File Upload Review**: Upload files directly for instant review
- **Admin API**: Manage API keys for access control

## API Endpoints

### Review API (`/api/v1/review`)
- `POST /` - Review code sent in request body
- `POST /upload` - Upload a file for review

### GitHub API (`/api/v1/github`)
- `POST /analyze` - Analyze a GitHub repository
- `POST /analyze-pr` - Analyze a specific pull request

### Admin API (`/api/v1/admin`)
- `POST /api-keys` - Create a new API key
- `GET /api-keys` - List all API keys
- `DELETE /api-keys/{key_id}` - Delete an API key

## Authentication

All endpoints (except GitHub public endpoints) require an `X-API-Key` header.

## Quick Start

> **Project root:** `C:\Users\Hp\New folder (12)\`  
> The application code lives in `app\` — there is no `aireview\app\` subdirectory.

### 1. Configure environment

```powershell
Copy-Item .env.example .env
# Then edit .env and fill in:
#   DATABASE_URL, GROQ_API_KEY, API_KEY, ADMIN_API_KEY, SECRET_KEY
```

### 2. Create & activate virtual environment

```powershell
# Create (one time only)
python -m venv env311

# Activate manually (PowerShell)
.\env311\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

> If PowerShell blocks script execution, run once:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 3. Start the application

**Windows (PowerShell) — recommended:**
```powershell
# Activates venv and starts server in one command
.\start.ps1
```

Optional flags:
```powershell
.\start.ps1 -Port 9000          # custom port
.\start.ps1 -NoReload           # disable auto-reload (production)
.\start.ps1 -Env venv           # use a different venv folder
```

**Linux / macOS / WSL:**
```bash
bash scripts/run_local.sh
```

Once running, visit:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | Lapo |
| APP_ENV | Environment | development |
| APP_HOST | Server host | 0.0.0.0 |
| APP_PORT | Server port | 8000 |
| DATABASE_URL | MySQL connection string | - |
| REDIS_URL | Redis connection (optional) | redis://localhost:6379/0 |
| GROQ_API_KEY | Groq API key for LLM | - |
| GITHUB_TOKEN | GitHub PAT for API access | - |
| API_KEY | Default API key | - |
| ADMIN_API_KEY | Admin API key | - |
| SECRET_KEY | JWT secret | - |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry | 30 |
| LOG_LEVEL | Logging level | info |