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
        """Extract text from an image using PaddleOCR with strict robust parsing."""
        start_time = time.time()
        try:
            # 1. Image preparation
            if isinstance(image_input, str):
                img = Image.open(image_input).convert('RGB')
            elif isinstance(image_input, Image.Image):
                img = image_input.convert('RGB')
            else:
                img = Image.fromarray(image_input).convert('RGB')

            max_dim = 800
            if max(img.size) > max_dim:
                scale = max_dim / float(max(img.size))
                img = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)), Image.Resampling.LANCZOS)

            img_arr = np.array(img)
            
            # 2. OCR Execution
            result = self.ocr.ocr(img_arr)
            
            # 3. Robust Extraction (User Requested Safe Logic)
            detections = []
            text = ""
            
            # CRITICAL: Safe check for empty results to prevent IndexError on result[0]
            if not result or len(result) == 0 or not result[0]:
                logger.warning("[OCR WARNING] Empty or malformed PaddleOCR result")
                return {
                    "detections": [],
                    "text": "",
                    "latency": time.time() - start_time,
                    "provider": "PaddleOCR (Empty)"
                }

            try:
                # PaddleOCR for single image returns [[ [box, (text, conf)], ... ]]
                # Safely access the first (only) image's results
                raw_detections = result[0]
                
                # USER REQUESTED SNIPPET
                try:
                    text = " ".join(
                        [str(line[1][0]) for line in raw_detections if isinstance(line, (list, tuple)) and len(line) > 1 and isinstance(line[1], (list, tuple)) and len(line[1]) > 0]
                    )
                except Exception:
                    text = ""
                    logger.warning("[OCR WARNING] Failed during text line join")

                # Structured detections for spatial RAG
                for line in raw_detections:
                    if isinstance(line, (list, tuple)) and len(line) > 1 and line[1] and isinstance(line[1], (list, tuple)) and len(line[1]) > 1:
                        bbox = line[0]
                        if bbox and len(bbox) >= 1:
                            x_coords = [p[0] for p in bbox]
                            y_coords = [p[1] for p in bbox]
                            detections.append({
                                "text": str(line[1][0]),
                                "bbox": [
                                    round(min(x_coords) / img.size[0], 4),
                                    round(min(y_coords) / img.size[1], 4),
                                    round(max(x_coords) / img.size[0], 4),
                                    round(max(y_coords) / img.size[1], 4)
                                ],
                                "confidence": float(line[1][1])
                            })
            except Exception as e:
                logger.warning(f"[OCR WARNING] Non-fatal parsing error: {str(e)}")
            
            latency = time.time() - start_time
            logger.info(f"PaddleOCR process complete. Valid detections: {len(detections)}. Latency: {latency:.2f}s")
            
            return {
                "detections": detections,
                "text": text,
                "latency": latency,
                "provider": "PaddleOCR"
            }
            
        except Exception as e:
            logger.error(f"Critical PaddleOCR failure: {str(e)}")
            return {
                "detections": [],
                "text": "",
                "latency": time.time() - start_time,
                "provider": "PaddleOCR (Critical Fallback)"
            }
