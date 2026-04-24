import sys
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class PipelineError(Exception):
    """Base exception for the DocVQA pipeline."""
    pass

class OCRProcessingError(PipelineError):
    """Raised when an OCR operation fails or returns malformed data."""
    pass

class RetrievalError(PipelineError):
    """Raised when the vector search or indexing fails."""
    pass

class LLMError(PipelineError):
    """Raised when the LLM or OpenRouter API fails."""
    pass

def safe_pipeline_stage(stage_name):
    """
    Decorator to wrap a pipeline stage and catch exceptions gracefully.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[PIPELINE ERROR] Stage '{stage_name}' failed: {str(e)}")
                # Return a safe fallback or re-raise a specific exception
                if stage_name == "OCR":
                    return {"text": "", "detections": [], "latency": 0, "provider": "Error Fallback"}
                elif stage_name == "LLM":
                    return {"answer": "Cognition Error", "latency": 0}
                return None
        return wrapper
    return decorator
