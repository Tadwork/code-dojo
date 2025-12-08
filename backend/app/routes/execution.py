import subprocess
import tempfile
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ExecutionRequest(BaseModel):
    code: str
    language: str


class ExecutionResponse(BaseModel):
    output: str
    error: str = ""


@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    code = request.code
    language = request.language.lower()

    if language not in ["python", "javascript"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Only 'python' and 'javascript' are supported.",
        )

    try:
        if language == "python":
            # Write code to temp file to handle multi-line code better than -c
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file_path = f.name

            try:
                result = subprocess.run(
                    ["python3", temp_file_path], capture_output=True, text=True, timeout=5
                )
            finally:
                os.unlink(temp_file_path)

        elif language == "javascript":
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
                f.write(code)
                temp_file_path = f.name

            try:
                result = subprocess.run(
                    ["node", temp_file_path], capture_output=True, text=True, timeout=5
                )
            finally:
                os.unlink(temp_file_path)

        return ExecutionResponse(output=result.stdout, error=result.stderr)

    except subprocess.TimeoutExpired:
        return ExecutionResponse(output="", error="Execution timed out after 5 seconds")
    except Exception as e:
        return ExecutionResponse(output="", error=f"Execution error: {str(e)}")
