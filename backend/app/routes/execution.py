import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ExecutionRequest(BaseModel):
    code: str
    language: str


class ExecutionResponse(BaseModel):
    output: str
    error: str = ""


from app.services.piston import execute_source

@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    code = request.code
    language = request.language.lower()

    if language not in ["python", "javascript"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Only 'python' and 'javascript' are supported.",
        )

    result = await execute_source(language, code)
    return ExecutionResponse(output=result["output"], error=result["error"])
