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

For production deployment as a single Docker image:

```bash
docker build -t coddojo:latest .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=your-secret-key \
  coddojo:latest
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

## API Documentation (OpenAPI)

The CodeDojo API includes comprehensive OpenAPI (Swagger) documentation that is automatically generated from the FastAPI application.

### Accessing the Documentation

During development, the API documentation is available at:

- **Swagger UI (Interactive)**: http://localhost:8000/docs
  - Interactive API explorer where you can test endpoints directly
  - Includes request/response examples and schemas
  
- **ReDoc (Alternative UI)**: http://localhost:8000/redoc
  - Clean, readable documentation interface
  - Better for reading and understanding the API

- **OpenAPI JSON**: http://localhost:8000/api/openapi.json
  - Raw OpenAPI specification in JSON format
  - Useful for importing into API clients or tools

- **OpenAPI YAML**: http://localhost:8000/api/openapi.yaml
  - Raw OpenAPI specification in YAML format
  - Human-readable format for version control

### Generating Static OpenAPI Files

To generate static OpenAPI specification files for version control or external tools:

```bash
cd backend
uv run python scripts/generate_openapi.py
```

This will create:
- `backend/openapi/openapi.json` - JSON format
- `backend/openapi/openapi.yaml` - YAML format

### OpenAPI Features

The API documentation includes:

- **Comprehensive endpoint descriptions** with examples
- **Request/response schemas** with validation rules
- **Error responses** with status codes and descriptions
- **WebSocket documentation** with message format specifications
- **Tag-based organization** (sessions, websocket, health)
- **Server configurations** for development and production environments

### Using the OpenAPI Spec

The OpenAPI specification can be used with:

- **Postman**: Import the JSON/YAML file to create a collection
- **Insomnia**: Import for API testing
- **Code Generation**: Generate client SDKs using tools like `openapi-generator`
- **API Gateway**: Import into API management platforms
- **Documentation Tools**: Generate static documentation sites

## Database Schema

The application uses PostgreSQL with the following main table:

- **sessions**: Stores coding session data including code, language, and metadata

## Deployment

### Render Blueprints (Infrastructure as Code)

CodeDojo uses **Render Blueprints** for infrastructure-as-code (IaC) deployment. A Blueprint is a `render.yaml` file that defines and manages multiple resources (services, databases, environment groups) from a single YAML configuration.

#### Our Blueprint Configuration

The `render.yaml` file at the root of this repository defines:

1. **Web Service** (`coddojo`): 
   - Builds from our multi-stage Dockerfile
   - Serves both the FastAPI backend and React frontend
   - Automatically connects to the PostgreSQL database
   - Health checks at `/api/health`

2. **PostgreSQL Database** (`coddojo-db`):
   - Free tier instance for development
   - Automatically provides connection string to the web service
   - PostgreSQL 16

#### Deploying with Blueprints

1. **Initial Setup**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **New > Blueprint**
   - Connect your GitHub/GitLab repository
   - Select the branch (e.g., `main`)
   - Review and apply the Blueprint

2. **Updating Infrastructure**:
   - Modify `render.yaml` in your repository
   - Commit and push to your linked branch
   - Render automatically applies changes

### Environment Variables for Production

- `DATABASE_URL`: PostgreSQL connection string (automatically set by Blueprint)
- `ENVIRONMENT`: Set to `production`
- `SECRET_KEY`: Strong secret key for security
- `PORT`: Port number (default: 8000)

### Manual Deployment (Alternative)

For manual deployment without Blueprints, see `Agents.md` for detailed instructions.

## Development Guidelines

For AI-assisted development and best practices, see [Agents.md](./Agents.md).

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

