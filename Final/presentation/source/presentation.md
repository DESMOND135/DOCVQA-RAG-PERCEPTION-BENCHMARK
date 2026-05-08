# Systems-Level Reliability Evaluation for Document AI: Bridging the Perception-Cognition Gap

**Master's Defense Presentation**  
Academic Year 2025-2026

---

## 1. The Challenge: Reliability in Document AI
- **The Problem**: Enterprise applications demand a robust approach to data corruption when extracting information from complex PDFs (invoices, medical records, financial forms).
- **DocVQA Architecture**: We dynamically frame extraction as Document Visual Question Answering (DocVQA), using Large Language Models (LLMs) as the cognitive reasoning engine.
- **The Perception-Cognition Gap**: While LLMs are linguistically brilliant, they lack spatial awareness. They must rely on external perception layers to understand layouts.
- **Research Gap**: Current systems either flatten documents, losing layout structure (traditional OCR), or suffer from resolution-loss hallucinations due to input constraints (end-to-end VLMs).

---

## 2. Research Contributions
1. **Systems-Level Evaluation Framework**: Formalization of a reliability and robustness framework under high-complexity zero-shot conditions.
2. **Hybrid OCR-VLM Synchronization**: A dual-stream architecture fusing deterministic character parsing with semantic layout mapping.
3. **Hallucination Analysis**: Analyzing perception-induced failure modes in standalone Vision-Language Models on dense layouts.
4. **Comparative Benchmark**: Quantitative evaluation across traditional OCR, deep-learning OCR, standalone VLMs, and Hybrid approaches.
5. **Robustness Validation**: Demonstrating improved accuracy and grounded reasoning in dense tabular environments.

---

## 3. Methodology: Modular RAG Pipeline

![System Architecture](../../../results/diagrams_minimal/system_architecture.png)

- **Swappable Perception Layers**:
  - Tesseract (Traditional baseline)
  - PaddleOCR (Deep-learning layout detection)
  - VLM (End-to-end multimodal extraction)
  - Hybrid (Dual-stream synchronization)

---

## 4. Mathematical Foundations
- **ANLS**: Measures soft similarity (String edit distance with OCR noise tolerance).
- **Exact Match (EM)**: Absolute identity $sim(\mathbf{P}, \mathbf{G}) = 1$.
- **F1-Score**: Harmonic mean of Precision and Recall in retrieval context.
- **Cosine Similarity**: $sim(\mathbf{q}, \mathbf{c}) = \frac{\mathbf{q} \cdot \mathbf{c}}{\|\mathbf{q}\| \|\mathbf{c}\|}$.
- **Throughput [S/s]**: Scalability metric ($T_p = 1/L$).

---

## 5. The Hybrid Perception Strategy

![Hybrid Flow](../../../results/diagrams_minimal/hybrid_workflow.png)

- **Dual Stream Logic**:
  - Stream 1: Literal OCR character precision (PaddleOCR).
  - Stream 2: Semantic VLM layout understanding.
- **Goal**: Combining literal character grounding with spatial context.

---

## 6. Experimental Results

| Strategy | ANLS (Mean ± SD) | EM (Mean ± SD) | F1 (Mean ± SD) | Latency [s] |
| :--- | :---: | :---: | :---: | :---: |
| **Hybrid** | 0.24 ± 0.05 | 0.20 ± 0.04 | 0.30 ± 0.06 | 14.2 |
| **VLM** | 0.17 ± 0.04 | 0.10 ± 0.03 | 0.20 ± 0.05 | 4.2 |
| **Tesseract** | 0.17 ± 0.04 | 0.10 ± 0.02 | 0.30 ± 0.05 | 11.0 |
| **PaddleOCR** | 0.13 ± 0.03 | 0.00 ± 0.00 | 0.10 ± 0.02 | 52.3 |

*(Graphs demonstrating Latency vs ANLS tradeoffs are available in the repository `results/plots/`)*

---

## 7. Error Analysis and Hallucinations
- **Resolution-Loss Hallucinations**: Standalone VLMs probabilistically guess numbers when input patches are downsampled, generating plausible but incorrect answers.
- **Layout Fragmentation**: Traditional OCR reads *across* columns, degrading semantic relationships and poisoning the retrieval index.
- **Retrieval Ambiguity**: FAISS struggles with repeated values (e.g., "$0.00") in dense tables, retrieving the correct string from the wrong geometric row.

---

## 8. Conclusion, Limitations, and Future Work
- **Conclusion**: Fusing literal character grounding with semantic layout awareness is essential for suppressing resolution-loss hallucinations in multimodal tasks.
- **Limitations**: The Hybrid architecture exhibits significant computational overhead, and experiments were constrained by CPU limitations and a 50-document validation scale.
- **Benchmark Context**: Low absolute ANLS scores reflect the strict zero-shot evaluation protocol on high-complexity layouts, rather than model instability. Baseline models like LayoutLMv3 were omitted due to lack of task-specific fine-tuning resources.
- **Future Work**: Optimizing Dual-Stream latency via GPU-accelerated tensor processing and scaling across dense tabular-specific corpora (e.g., TabFact).
