# Large Language Model as a Tool for Automatic Extraction of Information from PDF Documents

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

## 3. Error Analysis
We identify four primary failure modes in document perception and linguistic reasoning:

*   **OCR Misreading:** Deterministic extraction errors where visually similar characters are confused (e.g., '0' vs 'O', '8' vs 'B', '1' vs 'l'). This typically occurs due to scanning artifacts or low-resolution source images.
*   **Layout Fragmentation:** Traditional OCR engines often "flatten" multi-column text into a single linear string, destroying row/column associations and leading to context scrambling.
*   **VLM Hallucination:** Occurs when Vision-Language Models are forced to process high-density text at low input resolutions. The model "guesses" values that appear visually plausible but are factually incorrect.
*   **Retrieval Errors:** Semantic mismatches where the vector database identifies a context segment that is linguistically similar to the query but does not contain the specific target data point.

---

## 4. Evaluation Framework
Performance is evaluated using three industry-standard DocVQA metrics, calculated with rigorous mathematical grounding:

### 4.1 Average Normalized Levenshtein Similarity (ANLS)
Measures character-level edit distance between prediction and truth, providing tolerance for minor OCR noise.
<p align="center">
  $$ANLS = \frac{1}{N} \sum_{i=1}^{N} \max_{g \in G_i} \left( 1 - \frac{NL(g, P_i)}{\max(|g|, |P_i|)} \right)$$
</p>

**Variable Definitions:**
*   $N$: Total number of samples in the DocVQA evaluation subset.
*   $G_i$: The set of valid ground-truth answer variants for sample $i$ (e.g., "400" and "$400").
*   $P_i$: The model's generated prediction for sample $i$.
*   $NL(g, P_i)$: Levenshtein edit distance — the minimum number of character edits needed to transform $g$ into $P_i$.
*   $SC$: The resulting Similarity Score ($0 \le SC \le 1$). If $SC < 0.5$, it is set to $0$ to penalize hallucinations.

### 4.2 Exact Match (EM)
A binary indicator defining absolute precision.
<p align="center">
  $$EM = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(P_i \in G_i)$$
</p>

**Variable Definitions:**
*   $\mathbb{I}$: Indicator function returning 1.0 if the prediction perfectly mirrors any ground-truth variant, else 0.0.
*   $N$: Total sample size.

### 4.3 F1-Score
The harmonic mean of precision and recall, measuring token-level overlap.
<p align="center">
  $$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
</p>

**Variable Definitions:**
*   **Precision:** Percentage of predicted tokens that exist within the ground truth.
*   **Recall:** Percentage of ground truth tokens that were successfully captured in the prediction.

### 4.4 Cosine Similarity (Semantic Alignment)
Measures the vector alignment between query $A$ and context chunk $B$.
<p align="center">
  $$\text{sim}(A, B) = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$
</p>

**Variable Definitions:**
*   $A, B$: Vector representations in the 384-dimensional semantic embedding space.
*   $\theta$: The mathematical angle between vectors ($sim = 1.0$ if $\theta = 0^\circ$).

---

## 5. File Structure
```text
project/
├── data/           # PDF samples and ground-truth benchmark data
├── src/            # Core source code
│   ├── ocr/        # PaddleOCR and Tesseract implementations
│   ├── vlm/        # Vision-Language Model interfaces
│   ├── retrieval/  # FAISS indexing and semantic search logic
│   ├── pipeline/   # Hybrid synchronization and RAG workflows
│   ├── evaluation/ # Accuracy (ANLS, EM) and Efficiency metric logic
│   ├── processing/ # Text chunking and image pre-processing
│   ├── llm/        # Language Model connector interfaces
│   ├── config/     # System and model configuration files
│   ├── logging/    # Custom logging utilities
│   ├── exception/  # project-specific error handling
│   └── utils/      # Helper scripts and conversion utilities
├── results/        # Quantitative evaluation logs and performance plots
├── logs/           # System-level execution logs
├── main.py         # Primary benchmark execution script
└── requirements.txt # Project dependencies
```

---

## 6. Selected References
1.  **DocVQA:** Matthew et al., "DocVQA: A Dataset for VQA on Document Images."
2.  **PaddleOCR:** "PP-OCR: A Practical Ultra Lightweight OCR System."
3.  **RAG Pipeline:** Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."
4.  **ANLS Metric:** Biten et al., "ICDAR 2019 Competition on Scene Text Visual Question Answering."

---
*Developed by Tifang Desmond Ngoe (2025-2026)*
*Czestochowa University of Technology*
