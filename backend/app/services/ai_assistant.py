"""AI Assistant service using Pollinations AI."""

import httpx
import logging

logger = logging.getLogger(__name__)

POLLINATIONS_API_URL = "https://text.pollinations.ai/openai"


async def generate_code(prompt: str, current_code: str, language: str) -> dict:
    """
    Generate or update code using Pollinations AI.
    
    Args:
        prompt: User's instruction (e.g., "Add error handling")
        current_code: The current code in the editor
        language: Programming language being used
    
    Returns:
        dict with 'code' (generated code) and 'error' (if any)
    """
    
    system_prompt = f"""You are a helpful coding assistant. You generate and modify {language} code.
When given existing code and an instruction, update the code according to the instruction.
When asked to create something new, generate clean, well-commented code.
IMPORTANT: Return ONLY the code without any markdown formatting, explanations, or code fences.
Do not include ```{language} or ``` - just the raw code."""

    if current_code.strip():
        user_message = f"""Here is my current {language} code:

{current_code}

Instruction: {prompt}

Please update the code according to the instruction. Return only the updated code."""
    else:
        user_message = f"""Create {language} code for: {prompt}

Return only the code, no explanations."""

    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Calling Pollinations AI for {language} code generation")
            response = await client.post(POLLINATIONS_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract content from OpenAI-compatible response
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                # Clean up any markdown code fences that might have been included
                content = clean_code_response(content, language)
                return {"code": content, "error": ""}
            
            return {"code": "", "error": "No response from AI"}
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Pollinations API error {e.response.status_code}: {e.response.text}")
            return {"code": "", "error": f"AI service error: {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Pollinations connection error: {e}")
            return {"code": "", "error": "AI service unavailable"}
        except Exception as e:
            logger.error(f"Pollinations error: {e}")
            return {"code": "", "error": str(e)}


def clean_code_response(content: str, language: str) -> str:
    """Remove markdown code fences if present."""
    content = content.strip()
    
    # Remove opening fence with language
    if content.startswith(f"```{language}"):
        content = content[len(f"```{language}"):].strip()
    elif content.startswith("```"):
        # Find end of first line
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1:].strip()
    
    # Remove closing fence
    if content.endswith("```"):
        content = content[:-3].strip()
    
    return content
