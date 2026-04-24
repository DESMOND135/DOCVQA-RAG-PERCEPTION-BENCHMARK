import requests
import os
import sys
import time
import json
import base64
from io import BytesIO
from PIL import Image
from src.config.config import CONFIG
from src.logging.logger import get_logger
from src.exception.custom_exception import APIError

logger = get_logger(__name__)

class OpenRouterClient:
    def __init__(self, api_key=CONFIG['openrouter_api_key'], model=CONFIG['llm_model']):
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        logger.info(f"Initialized OpenRouterClient with model: {model}")

    def _encode_image(self, image_input):
        """Convert image to base64."""
        try:
            if isinstance(image_input, str):
                with open(image_input, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            elif isinstance(image_input, Image.Image):
                buffered = BytesIO()
                image_input.save(buffered, format="PNG")
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
            else:
                return None
        except Exception as e:
            logger.error(f"Image encoding failed: {str(e)}")
            return None

    def generate_answer(self, context, question, image=None):
        """Send request to OpenRouter API with retry on rate limits."""
        start_time = time.time()
        max_retries = 3
        retry_delay = 15  # seconds to wait after a 429
        
        try:
            if not self.api_key:
                raise APIError("OpenRouter API Key not found. Please add it to your .env file.", sys)
            
            prompt_content = [
                {
                    "type": "text",
                    "text": (
                        f"Answer the following question using ONLY the provided context from the document. "
                        f"Do not guess or use information from outside the context. "
                        f"Return ONLY the direct answer. No introductory phrases or extra sentences. "
                        f"If the answer cannot be found in the provided text or image, return exactly 'Not found'.\n\n"
                        f"Question: {question}\n\n"
                        f"Context From Document:\n{context if context else 'No text provided.'}\n\n"
                        f"Answer:"
                    )
                }
            ]
            
            if image:
                base_64_image = self._encode_image(image)
                if base_64_image:
                    prompt_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base_64_image}"
                        }
                    })

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt_content}
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/docvqa-project",
                "X-Title": "DocVQA Research Project",
                "Content-Type": "application/json"
            }
            
            for attempt in range(max_retries):
                logger.info(f"[STAGE: LLM] Executing OpenRouter API call (attempt {attempt + 1}/{max_retries})...")
                sys.stdout.flush()
                response = requests.post(self.url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 429:
                    logger.warning(f"Rate limit hit. Waiting {retry_delay}s before retry...")
                    sys.stdout.flush()
                    time.sleep(retry_delay)
                    continue
                
                if response.status_code != 200:
                    logger.error(f"OpenRouter API Error {response.status_code}: {response.text}")
                
                response.raise_for_status()
                break
            else:
                raise APIError("Max retries exceeded due to rate limiting.", sys)
            
            result = response.json()
            choices = result.get('choices', [])
            if not choices:
                raise APIError("API returned empty choices list.", sys)
            answer = choices[0]['message']['content']
            
            latency = time.time() - start_time
            logger.info(f"OpenRouter generate_answer completed in {latency:.2f}s")
            sys.stdout.flush()
            
            return {
                "answer": answer.strip(),
                "latency": latency,
                "model": self.model
            }
        except APIError:
            raise
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {str(e)}")
            raise APIError(f"API generation error: {str(e)}", sys)
