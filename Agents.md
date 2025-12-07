# Agents.md - CodeDojo Development Guidelines

## Overview

This document provides comprehensive guidelines for AI-assisted coding agents working on **CodeDojo**, a collaborative environment for users to practice coding interviews. The application consists of a Python-based web backend using the `uv` package manager and an interactive React frontend using npm. All development must follow best practices in testing and be deployable to Render service as a single Docker image.

## Project Architecture

### Technology Stack
- **Backend**: Python 3.10+ with `uv` for dependency management
- **Frontend**: React with npm for package management
- **Deployment**: Single Docker image for Render service
- **Testing**: pytest (backend), Jest + React Testing Library (frontend)

### Recommended Project Structure

```
CodeDojo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI/Flask application entry point
│   │   ├── models/          # Data models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utility functions
│   │   └── config.py        # Configuration management
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── unit/            # Unit tests
│   │   ├── integration/     # Integration tests
│   │   └── conftest.py      # pytest configuration
│   ├── pyproject.toml       # uv project configuration
│   └── Dockerfile           # Backend Dockerfile (if needed separately)
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utility functions
│   │   ├── App.js           # Main App component
│   │   └── index.js         # Entry point
│   ├── public/              # Static assets
│   ├── package.json         # npm dependencies
│   └── Dockerfile           # Frontend Dockerfile (if needed separately)
├── Dockerfile               # Multi-stage Dockerfile for production
├── docker-compose.yml       # Local development setup
├── .dockerignore
├── .gitignore
└── README.md
```

## Backend Development with Python and `uv`

### Project Initialization

1. **Initialize with `uv`**: Use `uv` to create and manage the Python project:
   ```bash
   uv init --name CodeDojo
   ```

2. **Configure `pyproject.toml`**: Define project metadata and dependencies:
   ```toml
   [project]
   name = "CodeDojo"
   version = "0.1.0"
   description = "Collaborative coding interview practice platform"
   requires-python = ">=3.10"
   dependencies = [
       "fastapi>=0.104.0",
       "uvicorn[standard]>=0.24.0",
       "pydantic>=2.0.0",
       "python-multipart>=0.0.6",
       "websockets>=12.0",
       "python-jose[cryptography]>=3.3.0",
       "passlib[bcrypt]>=1.7.4",
       "python-dotenv>=1.0.0",
   ]

   [project.optional-dependencies]
   dev = [
       "pytest>=7.4.0",
       "pytest-cov>=4.1.0",
       "pytest-asyncio>=0.21.0",
       "httpx>=0.25.0",
       "ruff>=0.1.0",
       "mypy>=1.7.0",
       "pre-commit>=3.5.0",
   ]

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [tool.ruff]
   line-length = 100
   target-version = "py310"

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = ["test_*.py", "*_test.py"]
   python_classes = ["Test*"]
   python_functions = ["test_*"]
   addopts = "--cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80"
   ```

3. **Install Dependencies**: Use `uv sync` to install all dependencies:
   ```bash
   uv sync
   ```

### Code Quality Standards

1. **Linting and Formatting**: Always use `ruff` for linting and formatting:
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

2. **Type Checking**: Use `mypy` for static type checking:
   ```bash
   uv run mypy app/
   ```

3. **Pre-commit Hooks**: Set up pre-commit hooks to enforce code quality:
   ```bash
   uv run pre-commit install
   ```
   
   Create `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.1.0
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format
     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v1.7.0
       hooks:
         - id: mypy
           additional_dependencies: [types-all]
   ```

### Testing Best Practices

1. **Test Coverage Requirements**:
   - Minimum 80% code coverage for all backend code
   - All API endpoints must have integration tests
   - All business logic must have unit tests
   - Use `pytest-cov` to enforce coverage thresholds

2. **Test Structure**:
   ```python
   # tests/unit/test_services.py
   import pytest
   from app.services.coding_service import CodingService

   class TestCodingService:
       def test_execute_code_success(self):
           service = CodingService()
           result = service.execute_code("print('hello')", "python")
           assert result["status"] == "success"
           assert result["output"] == "hello"
       
       def test_execute_code_timeout(self):
           service = CodingService()
           result = service.execute_code("while True: pass", "python")
           assert result["status"] == "timeout"
   ```

3. **Integration Testing**:
   ```python
   # tests/integration/test_api.py
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app

   @pytest.fixture
   def client():
       return TestClient(app)

   def test_create_session(client):
       response = client.post("/api/sessions", json={"name": "Test Session"})
       assert response.status_code == 201
       assert response.json()["name"] == "Test Session"
   ```

4. **Running Tests**:
   ```bash
   # Run all tests with coverage
   uv run pytest --cov=app --cov-fail-under=80
   
   # Run specific test file
   uv run pytest tests/unit/test_services.py
   
   # Run with verbose output
   uv run pytest -v
   ```

5. **Test Fixtures**: Use `conftest.py` for shared fixtures:
   ```python
   # tests/conftest.py
   import pytest
   from app.main import app
   from fastapi.testclient import TestClient

   @pytest.fixture
   def client():
       return TestClient(app)

   @pytest.fixture
   def sample_user():
       return {"id": 1, "username": "testuser", "email": "test@example.com"}
   ```

## Frontend Development with React and npm

### Project Initialization

1. **Initialize React Project**: Use Create React App or Vite:
   ```bash
   npx create-react-app frontend
   # OR for faster builds
   npm create vite@latest frontend -- --template react
   ```

2. **Install Dependencies**: Essential packages for CodeDojo:
   ```bash
   cd frontend
   npm install axios react-router-dom socket.io-client
   npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
   ```

3. **Configure `package.json`**: Ensure proper scripts:
   ```json
   {
     "scripts": {
       "start": "react-scripts start",
       "build": "react-scripts build",
       "test": "react-scripts test --coverage --watchAll=false",
       "lint": "eslint src --ext .js,.jsx",
       "format": "prettier --write \"src/**/*.{js,jsx,json,css}\""
     }
   }
   ```

### Code Quality Standards

1. **ESLint Configuration**: Use ESLint with React best practices:
   ```json
   // .eslintrc.json
   {
     "extends": [
       "react-app",
       "react-app/jest"
     ],
     "rules": {
       "no-console": "warn",
       "no-unused-vars": "warn"
     }
   }
   ```

2. **Prettier Configuration**: Ensure consistent formatting:
   ```json
   // .prettierrc
   {
     "semi": true,
     "trailingComma": "es5",
     "singleQuote": true,
     "printWidth": 100,
     "tabWidth": 2
   }
   ```

### Testing Best Practices

1. **Component Testing**: Test all React components:
   ```javascript
   // src/components/__tests__/CodeEditor.test.js
   import { render, screen, fireEvent } from '@testing-library/react';
   import { CodeEditor } from '../CodeEditor';

   describe('CodeEditor', () => {
     it('renders code editor with initial value', () => {
       render(<CodeEditor initialValue="console.log('hello')" />);
       expect(screen.getByDisplayValue("console.log('hello')")).toBeInTheDocument();
     });

     it('calls onChange when code is modified', () => {
       const handleChange = jest.fn();
       render(<CodeEditor onChange={handleChange} />);
       const editor = screen.getByRole('textbox');
       fireEvent.change(editor, { target: { value: 'new code' } });
       expect(handleChange).toHaveBeenCalledWith('new code');
     });
   });
   ```

2. **Integration Testing**: Test component interactions:
   ```javascript
   // src/pages/__tests__/SessionPage.test.js
   import { render, screen, waitFor } from '@testing-library/react';
   import { SessionPage } from '../SessionPage';
   import { BrowserRouter } from 'react-router-dom';

   describe('SessionPage', () => {
     it('loads and displays session data', async () => {
       render(
         <BrowserRouter>
           <SessionPage />
         </BrowserRouter>
       );
       
       await waitFor(() => {
         expect(screen.getByText(/Session/i)).toBeInTheDocument();
       });
     });
   });
   ```

3. **API Service Testing**: Mock API calls:
   ```javascript
   // src/services/__tests__/api.test.js
   import { getSession } from '../api';
   import axios from 'axios';

   jest.mock('axios');

   describe('API Service', () => {
     it('fetches session data', async () => {
       const mockData = { id: 1, name: 'Test Session' };
       axios.get.mockResolvedValue({ data: mockData });
       
       const result = await getSession(1);
       expect(result).toEqual(mockData);
       expect(axios.get).toHaveBeenCalledWith('/api/sessions/1');
     });
   });
   ```

4. **Running Tests**:
   ```bash
   # Run all tests with coverage
   npm test -- --coverage --watchAll=false
   
   # Run specific test file
   npm test -- CodeEditor.test.js
   ```

5. **Coverage Requirements**:
   - Minimum 70% code coverage for frontend components
   - All user interactions must be tested
   - All API service calls must be mocked and tested

## Dockerization for Single Image Deployment

### Multi-Stage Dockerfile

Create a single Dockerfile that builds both frontend and backend:

```dockerfile
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Build Python backend
FROM python:3.10-slim AS backend-builder
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy backend files
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Copy backend source
COPY backend/ ./

# Run backend tests
RUN uv run pytest --cov=app --cov-fail-under=80 || exit 1

# Stage 3: Production image
FROM python:3.10-slim
WORKDIR /app

# Install uv and runtime dependencies
RUN pip install --no-cache-dir uv && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend from builder
COPY --from=backend-builder /app /app

# Copy frontend build from builder
COPY --from=frontend-builder /app/frontend/build /app/static

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Backend Configuration for Serving Static Files

Ensure the backend serves the React build files:

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="CodeDojo API")

# Mount static files (React build)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React app for all non-API routes"""
        if not full_path.startswith("api") and not full_path.startswith("static"):
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        return {"error": "Not found"}

# API routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# ... other API routes
```

### Docker Build and Test

1. **Build the Docker Image**:
   ```bash
   docker build -t coddojo:latest .
   ```

2. **Test the Docker Image Locally**:
   ```bash
   # Run container
   docker run -p 8000:8000 coddojo:latest
   
   # Test health endpoint
   curl http://localhost:8000/api/health
   
   # Test frontend is served
   curl http://localhost:8000/
   ```

3. **Create `.dockerignore`**:
   ```
   __pycache__
   *.pyc
   *.pyo
   *.pyd
   .Python
   env/
   venv/
   .venv
   node_modules/
   .git
   .gitignore
   .env
   .pytest_cache
   .coverage
   htmlcov/
   *.log
   .DS_Store
   ```

## Deployment to Render Service

### Render Configuration

1. **Create `render.yaml`** (optional, for infrastructure as code):
   ```yaml
   services:
     - type: web
       name: coddojo
       env: docker
       dockerfilePath: ./Dockerfile
       dockerContext: .
       envVars:
         - key: PORT
           value: 8000
         - key: ENVIRONMENT
           value: production
       healthCheckPath: /api/health
   ```

2. **Deploy via Render Dashboard**:
   - Go to Render Dashboard → New → Web Service
   - Connect your Git repository
   - Set the following:
     - **Name**: coddojo
     - **Environment**: Docker
     - **Dockerfile Path**: `./Dockerfile`
     - **Docker Context**: `.`
     - **Port**: 8000
     - **Health Check Path**: `/api/health`

3. **Environment Variables**: Set in Render Dashboard:
   - `PORT=8000` (required)
   - `ENVIRONMENT=production`
   - Any API keys or secrets needed

### Alternative: Deploy Prebuilt Docker Image

If building Docker images externally:

1. **Push to Container Registry**:
   ```bash
   # Tag image
   docker tag coddojo:latest your-registry/coddojo:latest
   
   # Push to registry
   docker push your-registry/coddojo:latest
   ```

2. **Deploy on Render**:
   - New → Web Service → Existing Image
   - Image URL: `your-registry/coddojo:latest`
   - Port: 8000
   - Health Check: `/api/health`

## Development Workflow for AI Agents

### Before Making Changes

1. **Understand Requirements**: Read the issue/task description carefully
2. **Check Existing Code**: Review related files and patterns
3. **Plan Implementation**: Consider testability and maintainability

### During Development

1. **Write Tests First** (TDD approach when possible):
   - Write failing tests
   - Implement feature
   - Ensure tests pass
   - Refactor if needed

2. **Follow Code Style**:
   - Run `uv run ruff format .` for Python
   - Run `npm run format` for JavaScript
   - Ensure type hints in Python
   - Use TypeScript or PropTypes for React

3. **Test Locally**:
   ```bash
   # Backend tests
   cd backend && uv run pytest
   
   # Frontend tests
   cd frontend && npm test
   
   # Full Docker build test
   docker build -t coddojo:test .
   ```

### After Making Changes

1. **Verify Tests Pass**:
   - All existing tests must pass
   - New tests must be added for new features
   - Coverage thresholds must be met

2. **Check Code Quality**:
   ```bash
   # Backend
   uv run ruff check .
   uv run mypy app/
   
   # Frontend
   npm run lint
   ```

3. **Test Docker Build**:
   ```bash
   docker build -t coddojo:test .
   docker run -p 8000:8000 coddojo:test
   ```

## Continuous Work and State Management

When working on CodeDojo over multiple sessions or when interrupted, agents must maintain continuity and preserve work state.

### State Preservation

1. **Commit Frequently**: Make atomic commits after completing logical units of work:
   ```bash
   git add <changed-files>
   git commit -m "feat: add user authentication endpoint"
   ```

2. **Document Progress**: Create or update `PROGRESS.md` or task tracking files:
   ```markdown
   # Progress Log
   
   ## 2024-01-15
   - [x] Set up backend project structure
   - [x] Implemented health check endpoint
   - [ ] Implement user authentication (in progress)
   - [ ] Add WebSocket support for real-time collaboration
   ```

3. **Use Feature Branches**: Create branches for significant features:
   ```bash
   git checkout -b feature/user-authentication
   # ... work on feature ...
   git commit -m "feat: implement user authentication"
   ```

4. **Save Checkpoints**: Before major refactoring or experimental work:
   ```bash
   git tag checkpoint-<description>-<date>
   git push origin checkpoint-<description>-<date>
   ```

### Resuming Work

1. **Check Git Status**: Always start by checking the current state:
   ```bash
   git status
   git log --oneline -10
   ```

2. **Review Recent Changes**: Understand what was done previously:
   ```bash
   git diff HEAD~1
   git log --stat -5
   ```

3. **Check for Uncommitted Work**: Look for uncommitted changes:
   ```bash
   git status
   git diff
   ```

4. **Read Documentation**: Review `PROGRESS.md`, `README.md`, and `Agents.md` for context

5. **Run Tests**: Verify the current state is working:
   ```bash
   cd backend && uv run pytest
   cd frontend && npm test
   ```

### Work Session Checklist

**At the Start of Each Session:**
- [ ] Check git status and recent commits
- [ ] Review any progress documentation
- [ ] Run tests to verify current state
- [ ] Understand the current task/objective
- [ ] Check for any blocking issues or dependencies

**During Work:**
- [ ] Make frequent, atomic commits
- [ ] Update progress documentation
- [ ] Run tests after significant changes
- [ ] Document any decisions or architectural choices

**At the End of Each Session:**
- [ ] Commit all completed work
- [ ] Push changes to remote repository
- [ ] Update progress documentation
- [ ] Document any incomplete work or next steps
- [ ] Note any blockers or issues encountered

### Progress Documentation Format

Create or maintain `PROGRESS.md` in the root directory:

```markdown
# CodeDojo Development Progress

## Current Status
[Brief description of current state]

## Recent Accomplishments
- [Date] - [What was completed]

## In Progress
- [Current task] - [Status/Notes]

## Next Steps
- [Immediate next task]
- [Future tasks]

## Blockers/Issues
- [Any blocking issues or questions]

## Technical Decisions
- [Date] - [Decision] - [Rationale]
```

## Multi-Agent Coordination

When multiple AI agents work on CodeDojo simultaneously, coordination is critical to avoid conflicts and ensure efficient collaboration.

### Task Division Strategy

1. **Domain Separation**: Divide work by domain boundaries:
   - **Backend Agent**: Focus on API endpoints, business logic, database models
   - **Frontend Agent**: Focus on React components, UI/UX, client-side state
   - **DevOps Agent**: Focus on Docker, deployment, CI/CD
   - **Testing Agent**: Focus on writing and maintaining tests

2. **File-Level Locking**: Agents should work on different files when possible:
   - If Agent A is working on `backend/app/routes/auth.py`, Agent B should work on `backend/app/routes/sessions.py`
   - Avoid simultaneous edits to the same file

3. **Feature-Based Division**: Assign complete features to single agents:
   - Agent A: User authentication feature (backend + frontend)
   - Agent B: Code execution feature (backend + frontend)
   - Agent C: Real-time collaboration (WebSocket implementation)

### Communication Protocol

1. **Use Git Branches**: Each agent should work on a separate branch:
   ```bash
   # Agent A
   git checkout -b agent-a/user-authentication
   
   # Agent B
   git checkout -b agent-b/code-execution
   ```

2. **Document Intentions**: Create `WORK_IN_PROGRESS.md` or use git commit messages:
   ```bash
   git commit -m "WIP: implementing user auth - working on JWT tokens"
   ```

3. **Coordinate API Contracts**: When backend and frontend agents work together:
   - Backend agent documents API endpoints in `API.md` or OpenAPI spec
   - Frontend agent implements against documented API
   - Both agents review and agree on API contract before implementation

4. **Share Test Results**: Agents should communicate test status:
   ```bash
   # After completing work, run tests and share results
   uv run pytest --cov=app > test-results.txt
   ```

### Conflict Resolution

1. **Prevent Conflicts**:
   - Work on different files/modules when possible
   - Use feature branches
   - Commit and push frequently
   - Pull latest changes before starting work

2. **Handle Merge Conflicts**:
   ```bash
   # When conflicts occur
   git pull origin main
   # Resolve conflicts manually
   git add <resolved-files>
   git commit -m "resolve: merge conflicts in <file>"
   ```

3. **Code Review Process**:
   - Agents should review each other's PRs/commits
   - Use clear commit messages explaining changes
   - Request clarification if code intent is unclear

### Coordination Checklist

**Before Starting Work:**
- [ ] Check for active branches from other agents
- [ ] Pull latest changes from main branch
- [ ] Identify which files/modules you'll be modifying
- [ ] Announce your work area (if using shared communication)

**During Work:**
- [ ] Commit frequently to your feature branch
- [ ] Update shared documentation if API contracts change
- [ ] Run tests to ensure no regressions
- [ ] Check for conflicts if pulling updates

**Before Merging:**
- [ ] Ensure all tests pass
- [ ] Update documentation if needed
- [ ] Rebase or merge latest main branch
- [ ] Resolve any conflicts
- [ ] Request review from other agents if applicable

### Shared Resources

1. **API Documentation**: Maintain `API.md` or OpenAPI spec:
   ```markdown
   # CodeDojo API Documentation
   
   ## Authentication
   POST /api/auth/login
   POST /api/auth/register
   
   ## Sessions
   GET /api/sessions
   POST /api/sessions
   ...
   ```

2. **Database Schema**: Maintain `SCHEMA.md`:
   ```markdown
   # Database Schema
   
   ## Users Table
   - id: UUID
   - username: String
   - email: String
   ...
   ```

3. **Environment Variables**: Document in `.env.example`:
   ```bash
   # Backend
   DATABASE_URL=postgresql://...
   SECRET_KEY=...
   
   # Frontend
   REACT_APP_API_URL=http://localhost:8000
   ```

### Agent Roles and Responsibilities

**Backend Agent:**
- Implement API endpoints
- Design database models
- Write backend tests
- Document API contracts
- Ensure backend code quality

**Frontend Agent:**
- Implement React components
- Design UI/UX
- Write frontend tests
- Integrate with backend API
- Ensure frontend code quality

**Full-Stack Agent:**
- Can work on both backend and frontend
- Must coordinate with specialized agents
- Should focus on complete features end-to-end

**Testing Agent:**
- Write comprehensive tests
- Maintain test coverage thresholds
- Identify edge cases
- Review test quality

**DevOps Agent:**
- Maintain Docker configuration
- Set up CI/CD pipelines
- Configure deployment
- Monitor build processes

### Best Practices for Multi-Agent Work

1. ✅ **Communicate Early**: Announce what you're working on
2. ✅ **Work in Parallel**: Use different files/modules when possible
3. ✅ **Test Independently**: Each agent should run relevant tests
4. ✅ **Merge Frequently**: Don't let branches diverge too much
5. ✅ **Document Changes**: Update shared documentation
6. ✅ **Respect Boundaries**: Don't modify files another agent is working on
7. ✅ **Review Code**: Agents should review each other's work when possible

## Best Practices Summary

### Testing
- ✅ Minimum 80% backend coverage, 70% frontend coverage
- ✅ All API endpoints must have integration tests
- ✅ All user-facing features must have component tests
- ✅ Tests must run in Docker build process
- ✅ Use fixtures and mocks appropriately

### Code Quality
- ✅ Use type hints in Python
- ✅ Use ESLint and Prettier for JavaScript
- ✅ Run linters before committing
- ✅ Follow PEP 8 (Python) and Airbnb (React) style guides

### Docker
- ✅ Multi-stage builds for smaller images
- ✅ Run tests during Docker build
- ✅ Use `.dockerignore` to exclude unnecessary files
- ✅ Health checks for production readiness

### Deployment
- ✅ Single Docker image for simplicity
- ✅ Environment variables for configuration
- ✅ Health check endpoint for monitoring
- ✅ Static file serving from backend

## Common Pitfalls to Avoid

1. ❌ **Don't skip tests** - All features must be tested
2. ❌ **Don't hardcode values** - Use environment variables
3. ❌ **Don't ignore type checking** - Catch errors early
4. ❌ **Don't commit large files** - Use `.gitignore` and `.dockerignore`
5. ❌ **Don't skip Docker build testing** - Always test locally first
6. ❌ **Don't mix concerns** - Keep backend and frontend logic separate
7. ❌ **Don't ignore security** - Validate inputs, use HTTPS in production

## References

- [uv Documentation](https://github.com/astral-sh/uv)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Testing Library](https://testing-library.com/react)
- [pytest Documentation](https://docs.pytest.org/)
- [Render Docker Deployment](https://render.com/docs/docker)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Last Updated**: 2024
**Maintained By**: AI Coding Agents
**Project**: CodeDojo - Collaborative Coding Interview Practice Platform

