# CodeDojo

A collaborative environment for users to practice coding interviews. CodeDojo provides real-time collaboration features, code execution, and interview-style problem sets to help developers prepare for technical interviews.

## Technology Stack

- **Backend**: Python 3.10+ with FastAPI, managed with `uv`
- **Frontend**: React with npm
- **Deployment**: Single Docker image for Render service
- **Testing**: pytest (backend), Jest + React Testing Library (frontend)

## Project Structure

```
CodeDojo/
├── backend/          # Python backend application
├── frontend/         # React frontend application
├── Dockerfile        # Multi-stage Dockerfile for production
├── docker-compose.yml # Local development setup
└── Agents.md         # Development guidelines for AI agents
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (for local development)
- Docker (for containerized deployment)
- `uv` package manager (`pip install uv`)

### Local Development

#### Backend Setup

1. **Set up PostgreSQL database**:
   ```bash
   # Create database (adjust connection string as needed)
   createdb coddojo
   ```

2. **Configure environment variables**:
   Create a `.env` file in the `backend/` directory from `backend/.env.example`:
   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/coddojo
   ENVIRONMENT=development
   SECRET_KEY=your-secret-key-here
   E2B_API_KEY=your-e2b-api-key-here
   ```

3. **Install dependencies and run**:
   ```bash
   cd backend
   uv sync --extra dev
   uv run uvicorn app.main:app --reload
   ```

   The backend will automatically create database tables on startup.

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will start on `http://localhost:3000` and proxy API/WebSocket traffic to `http://localhost:8000` by default.

If your backend runs somewhere else, set the proxy target before starting the frontend:

```bash
REACT_APP_PROXY_TARGET=http://localhost:8000 npm start
```

### Running Tests

#### Backend Tests

```bash
cd backend
uv run pytest --cov=app --cov-fail-under=80
```

#### Frontend Tests

```bash
cd frontend
npm test -- --coverage --watchAll=false
```

### Docker Development Setup

For local development with Docker Compose (includes PostgreSQL). Create `backend/.env` first so the backend receives `E2B_API_KEY`:

```bash
# Start all services (PostgreSQL, backend, frontend)
docker-compose up

# Or run in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

The services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

For Docker Compose, set `REACT_APP_PROXY_TARGET=http://backend:8000` for the frontend service so the dev server proxies through the Docker network.

### Docker Production Build

To build and run the production image locally:

```bash
docker build -t coddojo:latest .
docker run -p 8000:8000 --env-file backend/.env coddojo:latest
```

## Usage

1. **Create a Session**:
   - Visit the home page
   - Optionally provide a session title
   - Select a programming language
   - Click "Create Session"

2. **Share the Link**:
   - Copy the session link from the session page
   - Share it with candidates or interviewers

3. **Collaborate**:
   - All connected users see real-time code updates
   - Change the programming language to update syntax highlighting
   - Code changes are automatically synchronized

4. **Execute Code**:
   - Click "Run Code" in the output panel
   - Code is executed in an isolated E2B sandbox

## API Endpoints

- `POST /api/sessions` - Create a new coding session
- `GET /api/sessions/{session_code}` - Get session details
- `WS /ws/{session_code}` - WebSocket endpoint for real-time collaboration
- `GET /api/health` - Health check endpoint

## API Documentation

The interactive API documentation is automatically generated and available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

The application uses PostgreSQL with the following main table:

- **sessions**: Stores coding session data including code, language, and metadata

## Deployment

CodeDojo is configured for deployment on [Render](https://render.com) using Infrastructure as Code (IaC), with PostgreSQL provided externally by Supabase.

1.  Go to the Render Dashboard and select **New > Blueprint**.
2.  Connect your repository.
3.  Render will detect [render.yaml](./render.yaml) and create the `codedojo` web service.
4.  In the Render dashboard, set these service environment variables before deploying:
    - `DATABASE_URL`: your Supabase connection string
    - `E2B_API_KEY`: your E2B API key
5.  Do not commit production secrets to the repository. The blueprint intentionally leaves those values unsynced because the source is public.

## Development Guidelines

For AI-assisted development and best practices, see [Agents.md](./Agents.md).

## Acknowledgments

CodeDojo is built with the help of these amazing open-source projects and services:

- **[E2B](https://e2b.dev/)** - Secure cloud sandboxes used for server-side code execution in CodeDojo. The backend currently enables Python, JavaScript, and TypeScript execution through the E2B Python SDK.

- **[Pollinations AI](https://pollinations.ai)** - A free, open-source generative AI platform that powers our AI code generation assistant. No API key required.

## License

MIT

## Contributing

All contributions are welcome! Please open an issue or submit a pull request.
