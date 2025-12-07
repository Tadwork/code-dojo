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

### Docker Build

```bash
docker build -t coddojo:latest .
docker run -p 8000:8000 coddojo:latest
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
   - JavaScript code runs in a Web Worker for safety
   - Python code uses Pyodide (WebAssembly Python)

## API Endpoints

- `POST /api/sessions` - Create a new coding session
- `GET /api/sessions/{session_code}` - Get session details
- `WS /ws/{session_code}` - WebSocket endpoint for real-time collaboration
- `GET /api/health` - Health check endpoint

## Database Schema

The application uses PostgreSQL with the following main table:

- **sessions**: Stores coding session data including code, language, and metadata

## Deployment

See `Agents.md` for detailed deployment instructions to Render service.

### Environment Variables for Production

- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: Set to `production`
- `SECRET_KEY`: Strong secret key for security
- `PORT`: Port number (default: 8000)

## Development Guidelines

For AI-assisted development and best practices, see [Agents.md](./Agents.md).

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

