import pytesseract
from PIL import Image
import os
import sys
import time
from src.config.config import CONFIG
from src.logging.logger import get_logger
from src.exception.custom_exception import OCRError

logger = get_logger(__name__)

class TesseractOCR:
    def __init__(self):
        try:
            # Set the path to tesseract
            pytesseract.pytesseract.tesseract_cmd = CONFIG["tesseract_cmd"]
            logger.info(f"Initialized Tesseract OCR with path: {CONFIG['tesseract_cmd']}")
        except Exception as e:
            raise OCRError(f"Failed to initialize Tesseract: {str(e)}", sys)

    def extract_text(self, image_input):
        """Extract text from an image using Tesseract."""
        start_time = time.time()
        try:
            if isinstance(image_input, str):
                image = Image.open(image_input)
            else:
                image = image_input

            # Hash for caching
            if hasattr(image, 'tobytes'):
                img_hash = hash(image.tobytes())
            else:
                img_hash = hash(str(image))

            if not hasattr(self.__class__, '_cache'):
                self.__class__._cache = {}
                
            if img_hash in self.__class__._cache:
                logger.info("Retrieved TesseractOCR result from cache.")
                cached_res = self.__class__._cache[img_hash]
                return {
                    "text": cached_res,
                    "latency": 0.0,
                    "provider": "Tesseract (Cached)"
                }

            # Run OCR
            text = pytesseract.image_to_string(image)
            
            latency = time.time() - start_time
            logger.info(f"Tesseract OCR completed in {latency:.2f}s")
            
            self.__class__._cache[img_hash] = text
            
            return {
                "text": text,
                "latency": latency,
                "provider": "Tesseract"
            }
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            raise OCRError(f"Tesseract OCR error: {str(e)}", sys)
