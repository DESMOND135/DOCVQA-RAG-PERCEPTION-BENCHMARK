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
from src.utils.exceptions import safe_pipeline_stage

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
            index_size = 0
            
            if self.perception_type in ["Tesseract", "PaddleOCR", "Hybrid"]:
                # Perception stage
                logger.info(f"[STAGE: PERCEPTION] Initiating {self.perception_type} extraction...")
                avg_confidence = 1.0
                chunks = []
                
                try:
                    if self.perception_type == "Hybrid":
                        logger.info(f"  -> Parallel Stream A: PaddleOCR")
                        ocr_res = self.ocr.extract_text(image)
                        logger.info(f"  -> Parallel Stream B: VLM Layout Summary")
                        vlm_res = self.vlm.get_visual_description(image)
                        
                        ocr_latency = ocr_res["latency"] + vlm_res["latency"]
                        
                        # Structured Spatial Chunking for Hybrid
                        logger.info(f"[STAGE: CHUNKING] Synchronizing dual-stream data...")
                        ocr_chunks = self.chunker.chunk_spatially(ocr_res["detections"])
                        vlm_chunks = self.chunker.chunk_text(f"LAYOUT_SUMMARY: {vlm_res['description']}")
                        chunks = ocr_chunks + vlm_chunks
                        
                        if ocr_res["detections"]:
                            avg_confidence = sum([d["confidence"] for d in ocr_res["detections"]]) / len(ocr_res["detections"])

                    elif self.perception_type == "PaddleOCR":
                        ocr_result = self.ocr.extract_text(image)
                        ocr_latency = ocr_result["latency"]
                        logger.info(f"[STAGE: CHUNKING] Processing PaddleOCR spatial detections...")
                        chunks = self.chunker.chunk_spatially(ocr_result["detections"])
                        if ocr_result["detections"]:
                            avg_confidence = sum([d["confidence"] for d in ocr_result["detections"]]) / len(ocr_result["detections"])
                    
                    else: # Tesseract
                        ocr_result = self.ocr.extract_text(image)
                        text = ocr_result["text"]
                        ocr_latency = ocr_result["latency"]
                        logger.info(f"[STAGE: CHUNKING] Sequential text chunking...")
                        chunks = self.chunker.chunk_text(text)
                except Exception as e:
                    logger.error(f"[PIPELINE ERROR] Perception stage failed for {self.perception_type}: {str(e)}")
                    chunks = [f"System Error: {str(e)}"]

                if not chunks:
                    chunks = ["No content extracted from document."]
                
                # RAG pipeline
                try:
                    logger.info(f"[STAGE: EMBEDDING] Generating {len(chunks)} vector embeddings...")
                    embeddings = self.embedder.generate_embeddings(chunks)
                    
                    logger.info(f"[STAGE: INDEXING] Building FAISS vector space...")
                    indexing_time, index_size = self.retriever.build_index(chunks, embeddings)
                    
                    logger.info(f"[STAGE: RETRIEVAL] Executing semantic search for query...")
                    query_embedding = self.embedder.get_query_embedding(question)
                    relevant_chunks, retrieval_time = self.retriever.retrieve_relevant_chunks(query_embedding, k=3)
                    context = "\n---\n".join(relevant_chunks)
                    
                    if avg_confidence < 0.7:
                        context = f"WARNING: Perception reliability is low ({avg_confidence:.2f}). Please reason carefully.\n" + context

                    # LLM answering
                    try:
                        logger.info(f"[STAGE: COGNITION] Requesting LLM reasoning over {len(relevant_chunks)} chunks...")
                        llm_result = self.llm.generate_answer(context, question)
                        prediction = llm_result["answer"]
                        llm_latency = llm_result["latency"]
                    except Exception as e:
                        logger.error(f"[LLM ERROR] OpenRouter call failed: {str(e)}. Skipping LLM step.")
                        prediction = "Cognition Error (API Unavailable)"
                        llm_latency = 0
                except Exception as e:
                    logger.error(f"[PIPELINE ERROR] RAG stage failed: {str(e)}")
                    prediction = "RAG Error"

            elif self.perception_type == "VLM":
                try:
                    # Direct VLM QA (No RAG)
                    logger.info(f"[STAGE: VLM DIRECT] Native multimodal reasoning...")
                    vlm_result = self.vlm.extract_answer(image, question)
                    prediction = vlm_result["answer"]
                    llm_latency = vlm_result["latency"]
                    index_size = 0
                except Exception as e:
                    logger.error(f"[PIPELINE ERROR] VLM Direct extraction failed: {str(e)}")
                    prediction = "VLM Error"
            
            # Calculate metrics
            logger.info(f"[STAGE: EVALUATION] Computing ANLS/EM/F1 metrics...")
            anls = self.metrics.calculate_anls(ground_truth_list, prediction)
            em = self.metrics.calculate_em(ground_truth_list, prediction)
            f1 = self.metrics.calculate_f1(ground_truth_list, prediction)
            
            total_latency = time.time() - start_total
            peak_memory = (process.memory_info().rss / (1024 * 1024)) - start_memory
            
            logger.info(f"Sample processing complete. Total Time: {total_latency:.2f}s, ANLS: {anls:.2f}")
            
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

