# Large Language Model as a Tool for Automatic Extraction of Information from PDF Documents

In the modern digital landscape, a vast amount of actionable data is locked within unstructured formats, primarily scanned PDFs and image-based documents. Financial institutions, healthcare providers, and administrative sectors face the significant challenge of manually extracting structured information from complex layouts like invoices, medical reports, and legal contracts. Traditional template-based extraction methods are brittle and unable to adapt to the inherent spatial and textual diversity of these documents.

This repository implements an advanced system where **Large Language Models (LLMs)** serve as the central cognitive engine for automatic information extraction. By leveraging LLMs within a modular **Retrieval-Augmented Generation (RAG)** pipeline, the system can reason over document contents and retrieve specific data points via natural language queries, bypassing the limitations of rigid extraction templates.

## Academic Context

- **University**: Czestochowa University of Technology (Czestochowa, Poland)
- **Supervisor**: Prof. Piotr Duda

## Project Overview

The primary goal of this project is to develop a robust architecture for the automatic extraction of structured information from heterogenous PDF documents. The system transitions from raw pixels to cognitive reasoning using a three-stage approach:

1.  **Supporting Perception Layer**: To enable the LLM to "see" documents, we utilize various perception methods:
    *   **OCR (Tesseract & PaddleOCR)**: Converting visual text into machine-readable strings while attempting to preserve layout.
    *   **Vision-Language Models (VLM)**: Direct multimodal understanding of images.
    *   **Hybrid Approach**: A novel synchronization of OCR precision with VLM spatial awareness.
2.  **Retrieval-Augmented Generation (RAG)**: Extracted text and layout descriptions are vectorized and indexed into a FAISS database. This ensures that the LLM's answers are strictly grounded in the document's factual content.
3.  **Cognitive Reasoning (LLM)**: The LLM acts as the final decision-maker, synthesizing the retrieved context into precise, structured answers to user questions (e.g., extracting totals from an invoice or names from a form).

## Project Structure

![Repository Structure](results/diagrams_minimal/readme_structure.png)

The repository is organized as follows:

The codebase is organized into modular components to facilitate easy experimentation with different models.

| Component | File Path | Description |
| :--- | :--- | :--- |
| **OCR (Tesseract)** | `src/ocr/tesseract.py` | Wrapper for the traditional Tesseract OCR engine. |
| **OCR (PaddleOCR)** | `src/ocr/paddleocr.py` | Deep-learning based OCR with layout detection capabilities. |
| **Vision-Language Model** | `src/vlm/vlm_model.py` | Integration for multimodal models (e.g., LLaVA) for direct extraction. |
| **Hybrid Pipeline** | `src/pipeline/pipeline.py` | Core logic for merging OCR precision with VLM layout understanding. |
| **Retriever** | `src/retrieval/retriever.py` | Orchestration of FAISS vector search and retrieval logic. |
| **Embeddings** | `src/processing/embedding.py` | Text vectorization using SentenceTransformers. |
| **Preprocessing** | `src/processing/chunking.py` | Document segmentation and chunking strategies. |

## System Modularity

The system is built on three core pillars of modularity:
1. **Perception Independence**: Every perception strategy (Tesseract, PaddleOCR, VLM, Hybrid) implements a standardized interface, allowing them to be swapped in `main.py` without code modification.
2. **Retrieval Agnosticism**: The retrieval system operates on standardized embeddings, meaning any vector database or similarity metric can be integrated.
3. **Cognitive Flexibility**: The final reasoning layer (LLM) is decoupled from the extraction layer, ensuring compatibility with both local and API-based models.

## Evaluation Benchmark (DocVQA)

To quantify the system's performance, we utilize the **Document Visual Question Answering (DocVQA)** benchmark. This benchmark provides a standardized dataset of document images, questions, and ground truth answers, allowing us to evaluate the system across two primary domains:

### 1. Benchmark Metrics (Accuracy Layer)
These metrics measure how correctly the system extracts information compared to human-annotated ground truth.
- **ANLS**: Average Normalized Levenshtein Similarity (Industry standard for DocVQA).
  $$ANLS = \frac{1}{N} \sum_{i=1}^{N} \max_{g \in G_i} (SC(g, P_i))$$
- **EM / F1**: Exact Match identity and harmonic mean of Precision/Recall.
  *Units: Ratio [0-1]*

### 2. Additional Performance Metrics (Efficiency Layer)
These metrics evaluate the practical efficiency and infrastructure overhead of the perception strategies. They are critical for evaluating system performance in real-world deployment scenarios.
- **Latency**: End-to-end inference time per document. *Unit: Seconds [s]*
- **Throughput**: Processing rate of the pipeline. *Unit: Samples per Second [S/s]*
- **Memory**: Peak RSS memory allocation. *Unit: Megabytes [MB]*
- **Database**: Indexing overhead and retrieval latency. *Unit: Seconds [s]*

## Execution

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Setup**:
   Configure your `.env` file with any required API keys (if using non-local LLMs).
3. **Run Benchmark**:
   ```bash
   python main.py
   ```

## Error Analysis

Based on our research, the information extraction pipeline's failures (validated on the DocVQA benchmark) are categorized into four primary areas:

1.  **OCR Misinterpretation**: Character confusion (e.g., "0" as "O") which heavily impacts **Exact Match (EM)**.
2.  **Layout Fragmentation**: Incorrect reading order in multi-column or complex tabular documents.
3.  **Retrieval Ambiguity**: The system pulls the correct label but the incorrect value due to proximity in the vector space.
4.  **Output Normalization**: Information is correct but the format differs from the ground truth (e.g., "$1k" vs. "1000").

### Comparative Vulnerability Analysis
| Model | ANLS | EM | Latency [s] | Throughput [S/s] |
| :--- | :---: | :---: | :---: | :---: |
| **Hybrid** | 0.24 | 0.20 | 14.2 | 0.07 |
| **VLM** | 0.17 | 0.10 | 4.2 | 0.24 |
| **Tesseract** | 0.17 | 0.10 | 11.0 | 0.09 |
| **PaddleOCR** | 0.13 | 0.00 | 52.3 | 0.02 |

## Results

Aggregated metrics are automatically saved to `results/demo_summary.csv` and visualized in `results/plots/`. Key metrics include:
- **ANLS**: Average Normalized Levenshtein Similarity.
- **EM / F1**: Accuracy metrics for the final answer.
- **Latency / Throughput**: System efficiency benchmarks.
- **Memory**: Peak resource usage.

## Limitations

- **Latency**: The Dual-Stream Hybrid approach is computationally heavy, resulting in higher processing times (~14s) per document.
- **Hardware Dependency**: Without dedicated GPUs, deep-learning models (PaddleOCR and VLMs) become significant bottlenecks.
- **Retrieval Bottlenecks**: The system remains vulnerable if the FAISS embedding vectors fail to accurately retrieve the correct semantic chunk.
