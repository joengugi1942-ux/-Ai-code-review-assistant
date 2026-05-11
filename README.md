<div align="center">
  <img src="https://img.shields.io/badge/Lapo-AI%20Code%20Review%20Assistant-blue?style=for-the-badge&logo=robot" alt="Lapo Logo">

# 🤖 Meet Lapo

**AI Code Review Assistant** - Lapo is a FastAPI-powered AI Code Review Assistant designed to be your team's digital senior developer. By integrating directly with GitHub, Lapo analyzes pull requests in real-time to ensure your code is performant, secure, and idiomatic.

> *"Lapo doesn't just catch bugs; it helps you become a better coder."*

</div>

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

1. Copy `.env.example` to `.env` and configure:
    - `DATABASE_URL` - Database connection (SQLite default, PostgreSQL recommended for production)
    - `GROQ_API_KEY` - Your Groq API key
   - `GITHUB_TOKEN` - GitHub personal access token (optional)
   - `SECRET_KEY` - JWT secret key
   - `API_KEY` - Initial API key for access

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | AI Code Review Assistant |
| APP_ENV | Environment | development |
| APP_HOST | Server host | 0.0.0.0 |
| APP_PORT | Server port | 8000 |
| DATABASE_URL | SQLite/PostgreSQL connection string | sqlite+aiosqlite:///./ai_review.db |
| REDIS_URL | Redis connection (optional) | redis://localhost:6379/0 |
| GROQ_API_KEY | Groq API key for LLM | - |
| GITHUB_TOKEN | GitHub PAT for API access | - |
| API_KEY | Default API key | - |
| ADMIN_API_KEY | Admin API key | - |
| SECRET_KEY | JWT secret | - |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry | 30 |
| LOG_LEVEL | Logging level | info |