from sentence_transformers import SentenceTransformer
import sys
import time
import numpy as np
from src.config.config import CONFIG
from src.logging.logger import get_logger
from src.exception.custom_exception import EmbeddingError

logger = get_logger(__name__)

class EmbeddingService:
    def __init__(self, model_name=CONFIG['embedding_model']):
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized EmbeddingService with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformer: {str(e)}")
            raise EmbeddingError(f"Embedding setup error: {str(e)}", sys)

    def generate_embeddings(self, chunks):
        """Convert text chunks to embeddings."""
        start_time = time.time()
        try:
            if not chunks:
                return []
                
            if not hasattr(self.__class__, '_cache'):
                self.__class__._cache = {}
                
            embeddings = []
            chunks_to_embed = []
            chunk_indices = []
            
            
            for i, chunk in enumerate(chunks):
                if chunk in self.__class__._cache:
                    embeddings.append(self.__class__._cache[chunk])
                else:
                    embeddings.append(None)
                    chunks_to_embed.append(chunk)
                    chunk_indices.append(i)
            
            if chunks_to_embed:
                new_embeddings = self.model.encode(chunks_to_embed)
                for i, idx in enumerate(chunk_indices):
                    embeddings[idx] = new_embeddings[i]
                    self.__class__._cache[chunks_to_embed[i]] = new_embeddings[i]
            
            latency = time.time() - start_time
            logger.info(f"Generated/Retrieved {len(embeddings)} embeddings in {latency:.2f}s")
            
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Embedding error: {str(e)}", sys)

    def get_query_embedding(self, query):
        """Embed user query."""
        try:
            return self.model.encode([query])[0]
        except Exception as e:
            logger.error(f"Query embedding failed: {str(e)}")
            raise EmbeddingError(f"Query embedding error: {str(e)}", sys)
