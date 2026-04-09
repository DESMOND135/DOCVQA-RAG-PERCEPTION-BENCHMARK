import sys
import time
from src.config.config import CONFIG
from src.logging.logger import get_logger
from src.llm.openrouter_client import OpenRouterClient

logger = get_logger(__name__)

class VLMModel:
    def __init__(self, model_name=CONFIG.get('vlm_model', "google/gemini-flash-1.5-exp:free")):
        self.model_name = model_name
        self.client = OpenRouterClient(model=model_name)
        logger.info(f"Initialized VLMModel with {model_name}")

    def extract_answer(self, image, question, context=None):
        """Ask VLM directly using image and context."""
        start_time = time.time()
        try:
            # Pass empty context for pure VLM, OCR text for Hybrid
            result = self.client.generate_answer(context=context, question=question, image=image)
            
            latency = time.time() - start_time
            logger.info(f"VLM inference completed in {latency:.2f}s")
            
            return {
                "answer": result["answer"],
                "latency": latency,
                "provider": "VLM" if not context else "Hybrid"
            }
        except Exception as e:
            logger.error(f"VLM process failed: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "latency": time.time() - start_time,
                "provider": "VLM"
            }

    def get_visual_description(self, image):
        """Generate a visual summary of the document layout."""
        start_time = time.time()
        try:
            prompt = (
                "Extract only structured and relevant factual information from this document image. "
                "Focus strictly on key-value pairs and tabular data. "
                "Do not provide narrative descriptions or conversational analysis. "
                "Output must be strictly concise and formatted for direct data retrieval."
            )
            
            # Using Gemini Flash for fast, structured extraction
            result = self.client.generate_answer(question=prompt, image=image)
            
            latency = time.time() - start_time
            logger.info(f"VLM visual description completed in {latency:.2f}s")
            
            return {
                "description": result["answer"],
                "latency": latency
            }
        except Exception as e:
            logger.error(f"VLM description failed: {str(e)}")
            return {
                "description": f"Visual analysis error: {str(e)}",
                "latency": time.time() - start_time
            }
