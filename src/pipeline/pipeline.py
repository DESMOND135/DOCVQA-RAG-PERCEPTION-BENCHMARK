import sys
import time
import os
import psutil
from src.config.config import CONFIG
from src.logging.logger import get_logger
from src.ocr.tesseract import TesseractOCR
from src.ocr.paddleocr import PaddleOCRModule
from src.vlm.vlm_model import VLMModel
from src.processing.chunking import TextChunker
from src.processing.embedding import EmbeddingService
from src.retrieval.retriever import DocumentRetriever
from src.llm.openrouter_client import OpenRouterClient
from src.evaluation.metrics import MetricsEvaluator

logger = get_logger(__name__)

class DocVQAPipeline:
    def __init__(self, perception_type="Tesseract"):
        self.perception_type = perception_type
        
        # Setup perception model
        if perception_type == "Tesseract":
            self.ocr = TesseractOCR()
        elif perception_type == "PaddleOCR":
            self.ocr = PaddleOCRModule()
        elif perception_type in ["VLM", "Hybrid"]:
            self.vlm = VLMModel()
            if perception_type == "Hybrid":
                self.ocr = PaddleOCRModule()
        else:
            raise ValueError(f"Unsupported perception type: {perception_type}")
        
        self.chunker = TextChunker()
        self.embedder = EmbeddingService()
        self.retriever = DocumentRetriever()
        self.llm = OpenRouterClient()
        self.metrics = MetricsEvaluator()
        
        logger.info(f"Pipeline initialized with {perception_type}")

    def run(self, image, question, ground_truth_list):
        """
        Runs the full DocVQA pipeline for a single sample.
        """
        start_total = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / (1024 * 1024) # MB
        
        try:
            prediction = ""
            ocr_latency = 0
            retrieval_time = 0
            indexing_time = 0
            llm_latency = 0
            
            if self.perception_type in ["Tesseract", "PaddleOCR", "Hybrid"]:
                # Perception stage
                if self.perception_type == "Hybrid":
                    # Extract text and description
                    try:
                        ocr_res = self.ocr.extract_text(image)
                        vlm_res = self.vlm.get_visual_description(image)
                        
                        ocr_latency = ocr_res["latency"] + vlm_res["latency"]
                        
                        # Separate OCR and VLM content as distinct chunk sets
                        # This prevents cross-contamination within a single chunk
                        ocr_chunks = self.chunker.chunk_text(f"OCR_TEXT: {ocr_res['text']}")
                        vlm_chunks = self.chunker.chunk_text(f"VLM_STRUCTURED_DATA: {vlm_res['description']}")
                        chunks = ocr_chunks + vlm_chunks
                        
                        if not chunks or len("".join(chunks).strip()) < 5:
                            chunks = ["Input document text was too short or empty."]
                            
                        logger.info(f"Hybrid perception complete. OCR chunks: {len(ocr_chunks)}, VLM chunks: {len(vlm_chunks)}")
                    except Exception as e:
                        logger.warning(f"Hybrid sub-stage failed: {str(e)}. Falling back to available data.")
                        chunks = [f"Perception Error: {str(e)}"]

                else:
                    ocr_result = self.ocr.extract_text(image)
                    text = ocr_result["text"]
                    ocr_latency = ocr_result["latency"]
                    
                    chunks = self.chunker.chunk_text(text)
                    if not chunks or len(text.strip()) < 5: 
                        chunks = [f"Input document text was too short or empty. Raw content: {text[:100]}"]
                
                # RAG pipeline
                embeddings = self.embedder.generate_embeddings(chunks)
                indexing_time, index_size = self.retriever.build_index(chunks, embeddings)
                
                query_embedding = self.embedder.get_query_embedding(question)
                
                # Reduce noise: top_k=2 as requested for higher precision
                top_k = 2 
                relevant_chunks, retrieval_time = self.retriever.retrieve_relevant_chunks(query_embedding, k=top_k)
                context = "\n---\n".join(relevant_chunks)
                
                # LLM answering
                llm_result = self.llm.generate_answer(context, question)
                prediction = llm_result["answer"]
                llm_latency = llm_result["latency"]

            elif self.perception_type == "VLM":
                # Direct VLM QA (No RAG)
                vlm_result = self.vlm.extract_answer(image, question)
                prediction = vlm_result["answer"]
                llm_latency = vlm_result["latency"]
                index_size = 0
            
            # Calculate metrics
            anls = self.metrics.calculate_anls(ground_truth_list, prediction)
            em = self.metrics.calculate_em(ground_truth_list, prediction)
            f1 = self.metrics.calculate_f1(ground_truth_list, prediction)
            
            total_latency = time.time() - start_total
            peak_memory = (process.memory_info().rss / (1024 * 1024)) - start_memory
            
            return {
                "Model": self.perception_type,
                "Question": question,
                "Ground_Truth": str(ground_truth_list),
                "Prediction": prediction,
                "EM": em,
                "F1": f1,
                "ANLS": anls,
                "Total_Latency": total_latency,
                "OCR_Latency": ocr_latency,
                "Retrieval_Latency": retrieval_time,
                "LLM_Latency": llm_latency,
                "Indexing_Time": indexing_time,
                "Index_Size_KB": index_size,
                "Memory_Used_MB": peak_memory
            }
        except Exception as e:
            logger.error(f"Pipeline failure [{self.perception_type}]: {str(e)}")
            return {"Model": self.perception_type, "Error": str(e), "Prediction": "Analysis Failed"}

