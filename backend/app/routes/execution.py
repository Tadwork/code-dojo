from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.piston import execute_source, SUPPORTED_LANGUAGES

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

    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{language}'. Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}",
        )

    result = await execute_source(language, code)
    return ExecutionResponse(output=result["output"], error=result["error"])
