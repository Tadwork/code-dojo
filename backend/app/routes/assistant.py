"""AI Assistant routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_assistant import generate_code

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    code: str = ""
    language: str = "python"


class GenerateResponse(BaseModel):
    code: str
    error: str = ""


@router.post("/assistant/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate or update code using AI.
    
    - **prompt**: Instruction for the AI (e.g., "Add error handling", "Create a sorting function")
    - **code**: Current code in the editor (optional, for modifications)
    - **language**: Programming language
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    result = await generate_code(
        prompt=request.prompt,
        current_code=request.code,
        language=request.language
    )
    
    return GenerateResponse(code=result["code"], error=result["error"])
