import faiss
import numpy as np
import sys
import time
from src.config.config import CONFIG
from src.logging.logger import get_logger

logger = get_logger(__name__)

class DocumentRetriever:
    def __init__(self, vector_store_type=CONFIG['vector_store_type']):
        self.vector_store_type = vector_store_type
        self.index = None
        self.chunks = []
        logger.info(f"DocumentRetriever ready ({vector_store_type})")

    def build_index(self, chunks, embeddings):
        """Build a FAISS index and return (indexing_time, index_size_kb)."""
        start_time = time.time()
        try:
            if not chunks or len(embeddings) == 0:
                return 0, 0
            
            self.chunks = chunks
            d = embeddings[0].shape[0]
            
            # L2 distance index
            self.index = faiss.IndexFlatL2(d)
            self.index.add(np.array(embeddings).astype('float32'))
            
            indexing_time = time.time() - start_time
            # FAISS IndexFlatL2 size: ntotal * d * 4 bytes
            index_size_bytes = self.index.ntotal * d * 4
            index_size_kb = index_size_bytes / 1024
            
            logger.info(f"Indexed {len(embeddings)} chunks in {indexing_time:.4f}s. Size: {index_size_kb:.2f} KB")
            return indexing_time, index_size_kb
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {str(e)}")
            return 0, 0

    def retrieve_relevant_chunks(self, query_embedding, k=3):
        """Return (relevant_chunks, retrieval_latency)."""
        start_time = time.time()
        try:
            if self.index is None:
                return [], 0
            
            query_vector = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_vector, k)
            
            relevant_chunks = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]
            
            latency = time.time() - start_time
            return relevant_chunks, latency
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return [], 0
