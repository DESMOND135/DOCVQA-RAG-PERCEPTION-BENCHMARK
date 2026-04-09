# Large Language Model as a Tool for Automatic Extraction of Information from PDF Documents
**Master's Defense Presentation**  
Academic Year 2025-2026

---

## 1. The Challenge & Information Extraction as DocVQA
- Large volumes of complex PDF documents (invoices, forms, tables) exist.
- **The Thesis Focus**: We define information extraction dynamically as Document Visual Question Answering (DocVQA).
- **The Cognitive Tool**: Large Language Models (LLMs) act as the reasoning engine within a Retrieval-Augmented Generation (RAG) pipeline.
- **The Perception Gap**: LLMs are "visually blind" to PDF layouts. They require a perception layer (OCR/VLM) to ground their reasoning in the document's spatial reality.

---

## 2. Methodology: Modular RAG Pipeline

![System Architecture](../results/diagrams_minimal/system_architecture.png)

- **Swappable Perception Layers**:
  - Tesseract (Traditional baseline)
  - PaddleOCR (Layout-sensitive extraction)
  - VLM (End-to-end multimodal reasoning)
  - **Hybrid** (The Proposed Dual-Stream Solution)

---

## 3. The Proposed Solution: Hybrid Perception

![Hybrid Flow](../results/diagrams_minimal/hybrid_workflow.png)

- **Dual Stream Logic**:
  - **OCR Stream**: Literal character precision.
  - **VLM Stream**: High-level spatial layout understanding.
- **Goal**: Synchronizing text identity with geometric context to eliminate hallucinations.

---

## 4. Evaluation Metric: ANLS
- **Average Normalized Levenshtein Similarity (ANLS)**:
- Measures edit-distance between prediction and ground truth.
- Threshold-aware (penalizes hallucinations severely).
- Essential for scoring extraction fidelity in complex PDFs.

---

## 5. Accuracy Comparison

![Accuracy Metrics](../results/plots/accuracy_comparison.png)

- **Key Finding**: The **Hybrid** model significantly outperforms standalone strategies.
- **Insight**: Combining OCR grounding with VLM spatial context creates the most accurate info-extraction tool.

---

## 6. System Efficiency (Latency vs Throughput)

![Efficiency Analysis](../results/plots/efficiency_comparison.png)

- **Key Finding**: **VLM** is the fastest (lowest latency), while OCR-heavy pipelines suffer from sequential processing bottlenecks.
- **Throughput**: VLM offers ~3.4x higher throughput compared to the Hybrid baseline.

---

## 7. Resource Management: Peak Memory

![Memory Usage](../results/plots/memory_comparison.png)

- **Key Finding**: Tesseract is remarkably lightweight (~350MB).
- **Overhead**: Hybrid and VLM models require multi-gigabyte allocations for transformer weights and image tensors.

---

## 8. Database & Search Performance

![Database Performance](../results/plots/database_efficiency.png)

- **Key Finding**: Retrieval from FAISS is near-instantaneous.
- **Bottleneck**: The primary overhead in RAG for PDFs is **Indexing** (chunking and embedding) the extracted text.

---

## 9. Error Analysis: Why Models Fail
- **Spatial Resolution Loss**: VLMs blur dense tabular data, leading to hallucinations.
- **Layout Fragmentation**: Traditional OCR reads *across* column borders.
- **Retrieval Ambiguity**: Vector search pulls correct strings from incorrect geometric rows.

---

## 10. Conclusion & Future Work
- **Conclusion**: The Hybrid strategy is the gold standard for precision-critical PDF extraction.
- **Optimization**: Future work focuses on reducing Hybrid latency via hardware acceleration and model quantization.
