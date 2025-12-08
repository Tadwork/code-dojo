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
   Create a `.env` file in the `backend/` directory:
   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/coddojo
   ENVIRONMENT=development
   SECRET_KEY=your-secret-key-here
   ```

3. **Install dependencies and run**:
   ```bash
   cd backend
   uv sync
   uv run uvicorn app.main:app --reload
   ```

   The backend will automatically create database tables on startup.

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will start on `http://localhost:3000` and connect to the backend at `http://localhost:8000`.

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

For local development with Docker Compose (includes PostgreSQL):

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
   - Code is securely executed on the server (Node.js for JavaScript, Python environment for Python)

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

CodeDojo is configured for easy deployment on [Render](https://render.com) using Infrastructure as Code (IaC).

1.  Go to the Render Dashboard and select **New > Blueprint**.
2.  Connect your repository.
3.  Render will automatically detect the `render.yaml` file and configure the service and database.

## Development Guidelines

For AI-assisted development and best practices, see [Agents.md](./Agents.md).

## Acknowledgments

CodeDojo is built with the help of these amazing open-source projects and services:

- **[Piston](https://github.com/engineer-man/piston)** - A high-performance code execution engine that powers our server-side code execution, supporting 50+ programming languages. We use the free public API at [emkc.org](https://emkc.org).

- **[Pollinations AI](https://pollinations.ai)** - A free, open-source generative AI platform that powers our AI code generation assistant. No API key required.

## License

MIT

## Contributing

All contributions are welcome! Please open an issue or submit a pull request.
