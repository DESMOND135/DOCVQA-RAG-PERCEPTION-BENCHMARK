# Systems-Level Reliability Evaluation for Document AI: Bridging the Perception-Cognition Gap

**Master's Defense Presentation**  
Academic Year 2025-2026

---

## 1. The Challenge: Reliability in Document AI
- **The Problem**: Enterprise applications demand zero-tolerance for data corruption when extracting information from complex PDFs (invoices, medical records, financial forms).
- **DocVQA Architecture**: We dynamically frame extraction as Document Visual Question Answering (DocVQA), using Large Language Models (LLMs) as the cognitive reasoning engine.
- **The Perception-Cognition Gap**: While LLMs are linguistically brilliant, they are "visually blind". They must rely on external perception layers to understand spatial layouts.
- **The Evaluation Goal**: To establish a comprehensive systems-level evaluation framework that benchmarks extraction reliability, isolating the exact trade-offs between deterministic text precision and generative visual hallucinations.

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

| Strategy | ANLS | EM | Latency [s] | Retrieval [s] | Indexing [s] |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hybrid** | 0.24 | 0.20 | 14.2 | 0.045 | 0.12 |
| **VLM** | 0.17 | 0.10 | 4.2 | 0.005 | 0.12 |
| **Tesseract** | 0.17 | 0.10 | 11.0 | 0.045 | 0.12 |
| **PaddleOCR** | 0.13 | 0.00 | 52.3 | 0.045 | 0.12 |

*(Graphs demonstrating Latency vs ANLS tradeoffs are available in the repository `results/plots/`)*

---

## 6. Error Analysis
- **OCR Misreading**: Character confusion (`0` vs `O`) cascades into Exact Match (EM) failure.
- **Layout Fragmentation**: Traditional OCR reads *across* columns, isolating values from their headers.
- **Retrieval Ambiguity**: FAISS struggles with repeated values (e.g., "$0.00") in dense tables, retrieving the correct string from the wrong geometric row.
- **Formatting**: Predicting "$1k" instead of "1000".

---

## 7. Key Findings & System Robustness Conclusion
- **Hybrid Synchronization as the Gold Standard**: Fusing literal character grounding with semantic layout awareness is essential for suppressing resolution-loss hallucinations in mission-critical tasks.
- **VLM Limitations**: While standalone VLMs deliver high-throughput, their vulnerability to resolution-loss makes them structurally unreliable for exact-match financial precision.
- **Evaluation Impact**: This framework successfully quantifies the trade-offs between perception modalities, providing a verifiable path forward for robust industrial Document AI.
- **Future Work**: Optimizing Dual-Stream latency via GPU-accelerated asynchronous tensor processing.
