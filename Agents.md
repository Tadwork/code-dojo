# Agents.md - CodeDojo Development Guidelines

## Overview

This document provides comprehensive guidelines for AI-assisted coding agents working on **CodeDojo**, a collaborative environment for users to practice coding interviews. The application consists of a Python-based web backend using the `uv` package manager and an interactive React frontend using npm. All development must follow best practices in testing and be deployable to Render service as a single Docker image.

## Project Architecture

### Technology Stack
- **Backend**: Python 3.10+ with `uv` for dependency management
- **Frontend**: React with npm for package management

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
   - **MANDATORY**: All existing tests must pass
   - **MANDATORY**: New tests must be added for ALL new features/components
   - **MANDATORY**: Coverage thresholds must be met (80% backend, 70% frontend)
   - **MANDATORY**: Every new component/service/route must have corresponding unit tests
   - **MANDATORY**: Run tests locally before committing: `uv run pytest` and `npm test`

2. **Run Linters Before Committing** (**MANDATORY**):
   - **CRITICAL**: Linting MUST pass before committing and pushing code
   - **Backend**: Run `uv run ruff check .` and `uv run ruff format .` to ensure code quality
   - **Frontend**: Run `npm run lint` to catch ESLint violations
   - **MANDATORY**: Fix all linting errors before committing - do not commit code with linting violations
   - Linting catches common issues like:
     - Testing library best practices violations (e.g., multiple assertions in `waitFor`)
     - Code style inconsistencies
     - Potential bugs and anti-patterns
   - Set up pre-commit hooks to automatically run linters (see Pre-commit Hooks section)
   
   ```bash
   # Backend linting (MUST pass before commit)
   cd backend
   uv run ruff check .
   uv run ruff format .
   uv run mypy app/
   
   # Frontend linting (MUST pass before commit)
   cd frontend
   npm run lint
   ```

3. **Check Code Quality**:
   ```bash
   # Backend
   uv run ruff check .
   uv run mypy app/
   
   # Frontend
   npm run lint
   ```

4. **Test Docker Build**:
   ```bash
   docker build -t coddojo:test .
   docker run -p 8000:8000 coddojo:test
   ```

5. **Update Documentation**:
   - **ALWAYS check if README.md needs updating** after making changes
   - Update README.md if you:
     - Add new features or functionality
     - Change setup or installation steps
     - Modify environment variables or configuration
     - Add new dependencies
     - Change API endpoints or behavior
     - Update deployment procedures
   - Keep README.md current with the actual state of the application
   - Document any breaking changes or migration steps

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

4. **Read Documentation**: Review `PROGRESS.md`, `README.md`, and `AGENTS.md` for context

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

