
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import urllib.request
import urllib.error
import json
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Local AI Inference Platform",
    description="API for local LLM inference using Ollama",
    version="1.0.0"
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODEL_NAME = "qwen2.5:1.5b"
REQUEST_TIMEOUT = 60


# Validate incoming requests
class InferenceRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=10000,
        description="Text prompt to send to the language model"
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Prompt cannot contain only whitespace.")

        return value


# Application liveness check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "local-ai-inference-platform"
    }


# Backend readiness check
@app.get("/ready")
def readiness_check():
    ollama_request = urllib.request.Request(
        OLLAMA_TAGS_URL,
        method="GET"
    )

    try:
        with urllib.request.urlopen(
            ollama_request,
            timeout=5
        ) as response:

            if response.status == 200:
                return {
                    "status": "ready",
                    "ollama": "available"
                }

            raise HTTPException(
                status_code=503,
                detail="Ollama is not ready."
            )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Ollama readiness check failed")

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "ollama": "unavailable"
            }
        )


# Generate text using Ollama
@app.post("/generate")
def generate_text(request: InferenceRequest):

    ollama_data = {
        "model": MODEL_NAME,
        "prompt": request.prompt,
        "stream": False
    }

    json_data = json.dumps(ollama_data).encode("utf-8")

    ollama_request = urllib.request.Request(
        OLLAMA_URL,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        # Send request to Ollama
        with urllib.request.urlopen(
            ollama_request,
            timeout=REQUEST_TIMEOUT
        ) as response:

            response_data = response.read()
            result = json.loads(response_data.decode("utf-8"))

        # Validate expected Ollama response fields
        required_fields = [
            "response",
            "model",
            "total_duration",
            "load_duration",
            "prompt_eval_count",
            "prompt_eval_duration",
            "eval_count",
            "eval_duration"
        ]

        if not isinstance(result, dict):
            raise ValueError("Ollama response must be a JSON object.")

        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing response field: {field}")

        # Calculate inference metrics
        prompt_tokens = result["prompt_eval_count"]
        generated_tokens = result["eval_count"]

        prompt_duration = result["prompt_eval_duration"]
        generation_duration = result["eval_duration"]

        total_duration = result["total_duration"]
        load_duration = result["load_duration"]

        # Validate metric values
        numeric_values = [
            prompt_tokens,
            generated_tokens,
            prompt_duration,
            generation_duration,
            total_duration,
            load_duration
        ]

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value < 0
            for value in numeric_values
        ):
            raise ValueError("Ollama returned invalid metric values.")

        if not isinstance(result["response"], str):
            raise ValueError("Ollama returned an invalid response.")

        if not isinstance(result["model"], str):
            raise ValueError("Ollama returned an invalid model name.")

        # Convert nanoseconds to seconds
        prompt_seconds = prompt_duration / 1_000_000_000
        generation_seconds = generation_duration / 1_000_000_000

        total_seconds = total_duration / 1_000_000_000
        load_seconds = load_duration / 1_000_000_000

        # Calculate throughput
        prompt_speed = (
            prompt_tokens / prompt_seconds
            if prompt_seconds > 0 else 0
        )

        generation_speed = (
            generated_tokens / generation_seconds
            if generation_seconds > 0 else 0
        )

        logger.info(
            "Inference completed: model=%s prompt_tokens=%s generated_tokens=%s",
            result["model"],
            prompt_tokens,
            generated_tokens
        )

        # Return response and performance metrics
        return {
            "prompt": request.prompt,
            "response": result["response"],
            "model": result["model"],
            "metrics": {
                "total_duration_seconds": round(total_seconds, 6),
                "load_duration_seconds": round(load_seconds, 6),
                "prompt_tokens": prompt_tokens,
                "prompt_processing_seconds": round(prompt_seconds, 6),
                "prompt_tokens_per_second": round(prompt_speed, 2),
                "generated_tokens": generated_tokens,
                "generation_seconds": round(generation_seconds, 6),
                "generation_tokens_per_second": round(generation_speed, 2)
            }
        }

    # Ollama returned an HTTP error
    except urllib.error.HTTPError as e:
        logger.error("Ollama returned HTTP error %s", e.code)

        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an HTTP error: {e.code}"
        )

    # Direct timeout
    except (TimeoutError, socket.timeout):
        logger.error("Ollama request timed out")

        raise HTTPException(
            status_code=504,
            detail="Ollama inference request timed out."
        )

    # Connection failure or wrapped timeout
    except urllib.error.URLError as e:
        if isinstance(e.reason, (TimeoutError, socket.timeout)):
            logger.error("Ollama request timed out")

            raise HTTPException(
                status_code=504,
                detail="Ollama inference request timed out."
            )

        logger.error("Unable to connect to Ollama: %s", e.reason)

        raise HTTPException(
            status_code=503,
            detail="Unable to connect to Ollama."
        )

    # Invalid JSON or encoding
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.exception("Invalid response received from Ollama")

        raise HTTPException(
            status_code=502,
            detail="Ollama returned an invalid response."
        )

    # Unexpected response structure or metric values
    except (ValueError, TypeError, KeyError):
        logger.exception("Unexpected Ollama response format")

        raise HTTPException(
            status_code=502,
            detail="Ollama returned an unexpected response format."
        )

    # Unexpected application error
    except Exception:
        logger.exception("Unexpected inference service error")

        raise HTTPException(
            status_code=500,
            detail="An unexpected internal server error occurred."
        )
