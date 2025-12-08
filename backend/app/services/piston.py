import httpx
import logging
import os

# Use public Piston API by default, or allow override for self-hosted
PISTON_API_URL = os.environ.get("PISTON_URL", "https://emkc.org/api/v2/piston").rstrip("/")

logger = logging.getLogger(__name__)

async def ensure_languages_installed():
    """
    Verifies connectivity to the Piston API and logs available runtimes.
    For public API (emkc.org), languages are already installed.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            logger.info(f"Connecting to Piston API at {PISTON_API_URL}...")
            response = await client.get(f"{PISTON_API_URL}/runtimes")
            response.raise_for_status()
            runtimes = response.json()
            
            available = [f"{r['language']} v{r['version']}" for r in runtimes[:5]]
            logger.info(f"Piston API connected. Available runtimes: {', '.join(available)}...")
            
        except Exception as e:
            logger.error(f"Failed to connect to Piston API: {type(e).__name__}: {e}")

async def execute_source(language: str, code: str) -> dict:
    """
    Executes code using the Piston API.
    """
    
    # Map our language names to Piston's
    lang_map = {
        "python": "python",
        "javascript": "javascript" 
    }
    
    piston_lang = lang_map.get(language, language)
    
    payload = {
        "language": piston_lang,
        "version": "*",
        "files": [
            {
                "content": code
            }
        ],
        "stdin": "",
        "args": [],
        "compile_timeout": 10000,
        "run_timeout": 3000,
        "memory_limit": 128 * 1024 * 1024,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{PISTON_API_URL}/execute", json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Piston returns: { "run": { "stdout": "...", "stderr": "...", "code": 0, ... }, "language": ... }
            if "run" in data:
                return {
                    "output": data["run"]["stdout"],
                    "error": data["run"]["stderr"]
                }
            return {"output": "", "error": "Invalid response from execution engine"}
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Piston execution failed {e.response.status_code}: {e.response.text}")
            return {"output": "", "error": f"Execution failed: {e.response.text}"}
        except httpx.RequestError as e:
            logger.error(f"Piston connection error: {e}")
            return {"output": "", "error": "Execution service unavailable"}
        except Exception as e:
             logger.error(f"Piston execution error: {e}")
             return {"output": "", "error": str(e)}
