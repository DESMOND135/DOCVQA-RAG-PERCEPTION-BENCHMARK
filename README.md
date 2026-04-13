# LLM-DocExtractor: Hybrid Perception Framework for DocVQA

**Master's Thesis Project**  
**Student:** Tifang Desmond Ngoe  
**Supervisor:** Prof. Piotr Duda, Czestochowa University of Technology

---

## 1. Project Description
This repository implements a **Dual-Stream Hybrid Perception Pipeline** integrated into a **Retrieval-Augmented Generation (RAG)** framework. It is specifically designed to bridge the **Perception-Cognition Gap** in automated document understanding. 

While Large Language Models (LLMs) possess advanced reasoning capabilities, they remain "spatially blind" to complex document layouts (multi-column reports, dense financial tables). This system synchronizes deterministic character-level precision with visual layout awareness to enable grounded, hallucination-free information extraction from structured PDFs.

---

## 2. System Architecture
The framework is built on a modular, plug-and-play architecture consisting of three primary layers:

1.  **Perception Layer (Dual-Stream):**
    *   **Deterministic Stream:** Utilizes **PaddleOCR** (DBNet+SVTR) for high-resolution, bit-perfect alphanumeric extraction.
    *   **Generative Stream:** Utilizes a **Vision-Language Model (VLM)** to interpret the semantic "spatial roadmap" and visual hierarchy of the document.
2.  **Indexing Layer (RAG):**
    *   **Embeddings:** `all-MiniLM-L6-v2` (384-dimensional dense vectors).
    *   **Vector Store:** `FAISS` (Facebook AI Similarity Search) for optimized, sub-millisecond context retrieval.
3.  **Cognition Layer:**
    *   **Context Grounding:** Late-fusion merging of OCR sequences and VLM layout summaries.
    *   **Reasoning:** LLM-based answer synthesis grounded strictly in retrieved document evidence.

---

## 3. File Structure
```text
project/
├── data/           # PDF samples and ground-truth benchmark data
├── src/            # Core source code
│   ├── ocr/        # PaddleOCR and Tesseract implementations
│   ├── vlm/        # Vision-Language Model interfaces
│   ├── retrieval/  # FAISS indexing and semantic search logic
│   └── pipeline/   # Hybrid synchronization and RAG workflows
├── results/        # Quantitative evaluation logs and performance plots
├── logs/           # System-level execution logs
├── main.py         # Primary benchmark execution script
└── requirements.txt # Project dependencies
```

---

## 4. Methodology
*   **Optical Character Recognition:** Compares traditional **Tesseract** (heuristic-based) against **PaddleOCR** (deep-learning based) to established a precision baseline.
*   **Vision-Language Model:** Evaluates spatial awareness capabilities of multimodal models in isolation.
*   **Hybrid Approach:** Implements a novel synchronization mechanism where the LLM is prompted with both raw text and visual structural metadata.
*   **Late-Fusion Context Grounding:** Merges two parallel perception streams into a single, high-fidelity context buffer for retrieval.

---

## 5. Evaluation Framework
Performance is evaluated using three industry-standard DocVQA metrics:

1.  **Average Normalized Levenshtein Similarity (ANLS):**
    Calculates character-level edit distance between prediction and truth, providing tolerance for minor OCR noise while penalizing structural failures.
    $$ANLS = \frac{1}{N} \sum_{i=1}^{N} \max_{g \in G_i} \left( 1 - \frac{NL(g, P_i)}{\max(|g|, |P_i|)} \right)$$

2.  **Exact Match (EM):**
    A binary indicator of absolute precision, requiring a perfect character-for-character match.
    $$EM = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(P_i \in G_i)$$

3.  **F1-Score:**
    The harmonic mean of precision and recall, measuring the token-level overlap between the answer and the ground truth.
    $$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 6. Results Summary
Experimental results on the DocVQA benchmark highlight a critical trade-off:
*   **Hybrid Superiority:** The Hybrid model consistently achieves the highest accuracy across all metrics (**ANLS: 0.24, EM: 0.20**), outperforming standalone VLMs by over 40% in complex layout scenarios.
*   **VLM Efficiency:** Standalone VLMs offer superior throughput and lower latency, making them suitable for low-stakes semantic summaries.
*   **The Precision Tax:** The Hybrid system requires significantly higher computational resources (GPU memory) and exhibits higher latency to ensure literal character fidelity.

---

## 7. Limitations & Future Work
*   **Pilot Study Constraints:** Evaluated on a curated subset of the DocVQA benchmark; future work requires testing on massive, multi-million page datasets.
*   **Infrastructure:** Current results are bounded by single-GPU throughput limits.
*   **Future Directions:** Integration of real-time multi-page document streaming and agentic self-correction mechanisms for OCR noise.

---

## 8. Selected References
1.  **DocVQA:** Matthew et al., "DocVQA: A Dataset for VQA on Document Images."
2.  **PaddleOCR:** "PP-OCR: A Practical Ultra Lightweight OCR System."
3.  **RAG Pipeline:** Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."
4.  **ANLS Metric:** Biten et al., "ICDAR 2019 Competition on Scene Text Visual Question Answering."

---
*Developed by Tifang Desmond Ngoe (2025-2026)*
