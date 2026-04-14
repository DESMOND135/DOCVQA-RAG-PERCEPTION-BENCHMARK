# Hybrid Perception RAG: Bridging the Perception-Cognition Gap in Document Visual Question Answering

**Master's Defense Presentation**  
Academic Year 2025-2026

---

## 1. The Challenge & Information Extraction as DocVQA
- Large volumes of complex PDF documents (invoices, forms, tables) exist.
- **The Thesis Focus**: We define information extraction dynamically as Document Visual Question Answering (DocVQA)—asking questions over PDFs rather than using rigid templates.
- **The Cognitive Tool**: Large Language Models (LLMs) act as the central reasoning engine within a Retrieval-Augmented Generation (RAG) pipeline to ingest facts and generate answers.
- **The Perception Gap**: LLMs are linguistically brilliant but "visually blind." They require images to be processed through external perception strategies (OCR, VLM, Hybrid) to understand PDF spatial layouts before they can generate accurate answers.

---

## 2. Methodology: Modular RAG Pipeline

![System Architecture](../../../results/diagrams_minimal/system_architecture.png)

- **Swappable Perception Layers**:
  - Tesseract (Traditional baseline)
  - PaddleOCR (Deep-learning layout detection)
  - VLM (End-to-end multimodal extraction)
  - Hybrid (Dual-stream synchronization)

---

## 3. Mathematical Foundations
- **ANLS**: Measures soft similarity (String edit distance with OCR noise tolerance).
- **Exact Match (EM)**: Absolute identity $sim(\mathbf{P}, \mathbf{G}) = 1$.
- **F1-Score**: Harmonic mean of Precision and Recall in retrieval context.
- **Cosine Similarity**: $sim(\mathbf{q}, \mathbf{c}) = \frac{\mathbf{q} \cdot \mathbf{c}}{\|\mathbf{q}\| \|\mathbf{c}\|}$.
- **Throughput [S/s]**: Scalability metric ($T_p = 1/L$).

---

## 4. The Hybrid Perception Strategy

![Hybrid Flow](../../../results/diagrams_minimal/hybrid_workflow.png)

- **Dual Stream Logic**:
  - Stream 1: Literal OCR character precision (PaddleOCR).
  - Stream 2: Semantic VLM layout understanding.
- **Goal**: Combining literal character grounding with spatial context.

---

## 5. Experimental Results

| Strategy | ANLS | EM | Latency [s] |
| :--- | :---: | :---: | :---: |
| **Hybrid** | 0.24 | 0.20 | 14.2 |
| **VLM** | 0.17 | 0.10 | 4.2 |
| **Tesseract** | 0.17 | 0.10 | 11.0 |
| **PaddleOCR** | 0.13 | 0.00 | 52.3 |

*(Graphs demonstrating Latency vs ANLS tradeoffs are available in the repository `results/plots/`)*

---

## 6. Error Analysis
- **OCR Misreading**: Character confusion (`0` vs `O`) cascades into Exact Match (EM) failure.
- **Layout Fragmentation**: Traditional OCR reads *across* columns, isolating values from their headers.
- **Retrieval Ambiguity**: FAISS struggles with repeated values (e.g., "$0.00") in dense tables, retrieving the correct string from the wrong geometric row.
- **Formatting**: Predicting "$1k" instead of "1000".

---

## 7. Key Findings & Conclusion
- **Hybrid** is the gold standard for mission-critical accuracy, suppressing VLM hallucinations using OCR literal grounding.
- **VLM** is optimal for high-throughput, low-latency applications but cannot be trusted for financial precision.
- **Future Work**: Optimizing Dual-Stream latency via model quantization and GPU asynchronous execution.
