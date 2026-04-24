import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

is_fast_mode = os.getenv("FAST_MODE", "False").lower() == "true"

# Global settings
CONFIG = {
    "fast_mode": is_fast_mode,
    
    # Dataset settings
    "dataset_name": os.getenv("DATASET_NAME", "VLR-CVC/DocVQA-2026"),
    "sample_size": int(os.getenv("SAMPLE_SIZE", 2 if is_fast_mode else 50)),

    
    # OCR settings
    "tesseract_cmd": os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    "paddle_use_gpu": False,
    "paddle_lang": "en",
    
    # RAG settings
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 300 if is_fast_mode else 500,
    "chunk_overlap": 50,
    "vector_store_type": "faiss", # or "numpy"
    "top_k": 1 if is_fast_mode else 2,
    
    # LLM settings
    "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
    "llm_model": os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct:free"),
    
    # Storage paths
    "results_dir": os.path.join(os.getcwd(), "results"),
    "plots_dir": os.path.join(os.getcwd(), "results", "plots"),
    "data_dir": os.path.join(os.getcwd(), "data"),
}

# Create folders if missing
os.makedirs(CONFIG["results_dir"], exist_ok=True)
os.makedirs(CONFIG["plots_dir"], exist_ok=True)
os.makedirs(CONFIG["data_dir"], exist_ok=True)
