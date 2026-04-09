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
        """Split text into chunks."""
        try:
            if not text:
                return []
            
            chunks = []
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunks.append(text[start:end])
                start += (self.chunk_size - self.chunk_overlap)
                
            logger.info(f"Generated {len(chunks)} chunks from text.")
            return chunks
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            return [text] # Fallback to original text
