import sys
from src.config.config import CONFIG
from src.logging.logger import get_logger

logger = get_logger(__name__)

class TextChunker:
    def __init__(self, chunk_size=CONFIG['chunk_size'], chunk_overlap=CONFIG['chunk_overlap']):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Initialized TextChunker with size: {chunk_size}, overlap: {chunk_overlap}")

    def chunk_text(self, text):
        """Split plain text into chunks."""
        try:
            if not text:
                return []
            
            chunks = []
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunks.append(text[start:end])
                start += (self.chunk_size - self.chunk_overlap)
                
            return chunks
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            return [text]

    def chunk_spatially(self, detections, group_by_line=True):
        """
        Group OCR detections into logical chunks based on spatial proximity.
        Each chunk is a JSON string containing text and aggregated bounding boxes.
        """
        try:
            if not detections:
                return []
            
            # Simple heuristic: Group by lines (sharing similar y-coordinates)
            # or group into fixed-count blocks to maintain spatial metadata
            chunks = []
            current_group = []
            
            # Basic spatial grouping logic
            for det in detections:
                # Store text + metadata as a single unit
                # We limit the number of items per chunk to keep the LLM context focused
                current_group.append(det)
                
                if len(current_group) >= 5: # Group every 5 detections
                    # Aggregate text and metadata
                    chunk_text = " ".join([d["text"] for d in current_group])
                    # Aggregate bbox (surrounding box)
                    bboxes = [d["bbox"] for d in current_group]
                    outer_bbox = [
                        min([b[0] for b in bboxes]),
                        min([b[1] for b in bboxes]),
                        max([b[2] for b in bboxes]),
                        max([b[3] for b in bboxes])
                    ]
                    
                    # Store as structured JSON-like string for the LLM
                    # This is the "intertwined" part: text + coordinates
                    chunks.append(f'{{"text": "{chunk_text}", "bbox": {outer_bbox}}}')
                    current_group = []
            
            # Add remaining
            if current_group:
                chunk_text = " ".join([d["text"] for d in current_group])
                bboxes = [d["bbox"] for d in current_group]
                outer_bbox = [min([b[0] for b in bboxes]), min([b[1] for b in bboxes]), max([b[2] for b in bboxes]), max([b[3] for b in bboxes])]
                chunks.append(f'{{"text": "{chunk_text}", "bbox": {outer_bbox}}}')

            logger.info(f"Generated {len(chunks)} spatial chunks from {len(detections)} detections.")
            return chunks
        except Exception as e:
            logger.error(f"Spatial chunking failed: {str(e)}")
            return ["Error in spatial processing."]
