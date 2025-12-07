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
- Docker (for containerized deployment)
- `uv` package manager (`pip install uv`)

### Local Development

#### Backend Setup

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
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

### Docker Build

```bash
docker build -t coddojo:latest .
docker run -p 8000:8000 coddojo:latest
```

## Deployment

See `Agents.md` for detailed deployment instructions to Render service.

## Development Guidelines

For AI-assisted development and best practices, see [Agents.md](./Agents.md).

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

