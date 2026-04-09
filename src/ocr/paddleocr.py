import os
import sys
import time
import numpy as np

os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_use_onednn'] = '0'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from paddleocr import PaddleOCR
from PIL import Image
from src.config.config import CONFIG
from src.logging.logger import get_logger
from src.exception.custom_exception import OCRError

logger = get_logger(__name__)

class PaddleOCRModule:
    def __init__(self, lang=CONFIG['paddle_lang'], use_gpu=CONFIG['paddle_use_gpu']):
        try:
            import os
            os.environ['FLAGS_use_mkldnn'] = '0'
            os.environ['FLAGS_use_onednn'] = '0'
            
            # Disable MKL-DNN to avoid Windows compatibility issues
            self.ocr = PaddleOCR(lang=lang, enable_mkldnn=False)
            logger.info(f"Initialized PaddleOCR with lang: {lang}")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            raise OCRError(f"PaddleOCR setup error: {str(e)}", sys)

    def extract_text(self, image_input):
        """Extract text from an image using PaddleOCR."""
        start_time = time.time()
        try:
            # Load and Resize for stability
            if isinstance(image_input, str):
                img = Image.open(image_input).convert('RGB')
            elif isinstance(image_input, Image.Image):
                img = image_input.convert('RGB')
            else:
                img = Image.fromarray(image_input).convert('RGB')

            # Dynamic resizing: prevents OOM on large DocVQA images
            max_dim = 800
            if max(img.size) > max_dim:
                scale = max_dim / float(max(img.size))
                new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image for PaddleOCR stability: {new_size}")

            img_arr = np.array(img)

            if hasattr(image_input, 'tobytes'):
                img_hash = hash(image_input.tobytes())
            elif isinstance(img_arr, np.ndarray):
                img_hash = hash(img_arr.tobytes())
            else:
                img_hash = hash(str(image_input))
                
            if not hasattr(self.__class__, '_cache'):
                self.__class__._cache = {}
                
            if img_hash in self.__class__._cache:
                logger.info("Retrieved PaddleOCR result from cache.")
                cached_res = self.__class__._cache[img_hash]
                return {
                    "text": cached_res,
                    "latency": 0.0,
                    "provider": "PaddleOCR (Cached)"
                }

            # Run OCR
            result = self.ocr.ocr(img_arr)
            
            # Join all detected text lines
            extracted_text = ""
            for line in result:
                if line:
                   for res in line:
                       extracted_text += res[1][0] + " "
            
            latency = time.time() - start_time
            logger.info(f"PaddleOCR completed in {latency:.2f}s")
            
            final_text = extracted_text.strip()
            self.__class__._cache[img_hash] = final_text
            
            return {
                "text": final_text,
                "latency": latency,
                "provider": "PaddleOCR"
            }
        except Exception as e:
            logger.error(f"PaddleOCR process failed: {str(e)}")
            raise OCRError(f"PaddleOCR error: {str(e)}", sys)
