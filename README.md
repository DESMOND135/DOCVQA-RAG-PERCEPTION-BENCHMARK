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

## Performance Comparison of Models

The following table summarizes the performance of each perception strategy across accuracy, efficiency, and resource utilization dimensions.

| Model | ANLS | EM | F1 Score | Latency [s] | Throughput [S/s] | Memory [MB] | Retrieval [s] | Indexing [s] | Index Size [KB] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hybrid** | **0.24** | **0.20** | **0.30** | 14.2 | 0.07 | 4600 | 0.05 | 0.12 | 1.5 |
| **VLM** | 0.17 | 0.10 | 0.20 | **4.2** | **0.24** | 4100 | 0.00 | 0.00 | 0.0 |
| **Tesseract** | 0.17 | 0.10 | **0.30** | 11.0 | 0.09 | **350** | 0.05 | 0.12 | 1.5 |
| **PaddleOCR** | 0.13 | 0.00 | 0.10 | 52.3 | 0.02 | 850 | 0.05 | 0.12 | 1.5 |

### Metric Explanations

- **Accuracy (Correctness)**: 
  - **ANLS / EM / F1**: Measure how closely the system's generated answer matches the human-annotated ground truth. Higher values indicate better information extraction quality.
- **Efficiency (Processing Speed)**:
  - **Latency**: The time required to process a single document from ingestion to answer.
  - **Throughput**: The number of documents processed per second.
- **Resource Usage**:
  - **Memory Usage**: The peak Resident Set Size (RSS) footprint during inference, indicating hardware requirements.
- **Database Performance**:
  - **Retrieval Latency**: Time to execute the FAISS similarity search.
  - **Indexing Time**: Time to chunk and embed the document text into the vector store.
  - **Index Size**: Storage footprint of the resulting vector embeddings.

### Result Interpretation

The experimental results reveal critical trade-offs between precision and speed in the information extraction pipeline:

- **Accuracy**: The **Hybrid** model achieves the highest ANLS (0.24), confirming that synchronizing literal OCR data with VLM spatial context provides the best answer quality and effectively reduces hallucinations.
- **Efficiency**: The **VLM** is the fastest configuration (4.2s latency), significantly outperforming OCR-based methods by sidestepping the text detection and vector indexing stages.
- **Trade-off Analysis**:
  - **The Hybrid Strategy** offers superior accuracy but incurs higher computational costs (14.2s latency) and the largest memory footprint.
  - **The VLM Strategy** serves as a high-speed alternative for scenarios where throughput is prioritized over absolute character precision.
  - **Tesseract** provides a remarkably efficient, lightweight baseline for simple layouts.
  - **PaddleOCR** demonstrates the highest cost-to-performance ratio in this specific CPU-only evaluation setup.

## System Configuration & Technical Details

This section describes the internal architecture and data flow of the automatic information extraction pipeline.

### Pipeline Flow

```mermaid
graph LR
    A[Document] --> B[OCR / VLM]
    B --> C[Text Chunking]
    C --> D[Embeddings]
    D --> E[FAISS Retrieval]
    E --> F[LLM Reasoning]
    F --> G[Grounded Answer]
```

### 1. Supporting Perception Layer
The system uses swappable modules (Tesseract, PaddleOCR, VLM, or Hybrid) to extract textual and visual data. This layer converts raw pixels into machine-readable context.

### 2. Chunking Strategy
To ensure the Large Language Model remains focused and within token limits, the extracted text is segmented using a recursive strategy:
- **Chunk Size**: 500 characters.
- **Overlap**: 50 characters.
- **Purpose**: Moving windows with overlap ensure that information at the borders of segments is not contextually destroyed, maintaining continuity during retrieval.

### 3. Embedding Model (Semantic Representation)
- **Model**: `SentenceTransformers (all-MiniLM-L6-v2)`.
- **Role**: This model maps text segments into a 384-dimensional dense vector space. Similar meanings are mapped closer together, enabling the system to understand relationships between concepts (e.g., "Total" and "Final Amount").

### 4. Vector Database (FAISS)
- **Storage**: We use **Facebook AI Similarity Search (FAISS)** as the high-performance indexing backend.
- **Efficiency**: It allows for sub-millisecond similarity search across potentially massive document repositories by organizing embeddings into navigable mathematical structures.

### 5. Retrieval & Similarity Search
- **Method**: `Cosine Similarity`.
- **Distinction**: Unlike traditional keyword search which looks for exact word matches, the system performs **semantic search**. It finds and retrieves the top-k most relevant chunks based on the mathematical "angle" between the user's question and the document context.

### 6. Cognitive Layer (LLM)
- **API**: `OpenRouter`.
- **Primary Model**: `Mistral-7B-Instruct (v0.2)`.
- **Role**: The LLM serves as the cognitive reasoning engine. It does not perform raw extraction; instead, it reads the retrieved chunks and generates a natural language answer that is strictly grounded in the provided document evidence.

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

## Limitations

- **Latency**: The Dual-Stream Hybrid approach is computationally heavy, resulting in higher processing times (~14s) per document.
- **Hardware Dependency**: Without dedicated GPUs, deep-learning models (PaddleOCR and VLMs) become significant bottlenecks.
- **Retrieval Bottlenecks**: The system remains vulnerable if the FAISS embedding vectors fail to accurately retrieve the correct semantic chunk.
