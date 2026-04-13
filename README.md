# LLM-DocExtractor: Hybrid Perception RAG

## Overview
A Master's Thesis project implementing a novel **Hybrid Perception Layer** for Document Visual Question Answering (DocVQA). This research addresses the **"Perception-Cognition Gap"** in document intelligence by synchronizing deterministic character-level precision with visual layout awareness within a Retrieval-Augmented Generation (RAG) framework.

## Key Architecture
1. **Hybrid Perception:** Synchronizes literal OCR tokens (**PaddleOCR**) with semantic layout descriptions (**Vision-Language Model**). This "Dual-Stream" approach eliminates the resolution-induced hallucinations common in standalone multimodal models.
2. **RAG Pipeline:** Utilizes `SentenceTransformers (all-MiniLM-L6-v2)` for 384-dimensional dense embeddings and `FAISS` for sub-millisecond context retrieval.
3. **Cognition:** Leverages Instruct-tuned LLMs to synthesize grounded answers based strictly on retrieved, layout-aware evidence.

## Mathematical Framework
We formalize document understanding through the following "Diamond-Standard" metrics:

<p align="center">
  <b>Average Normalized Levenshtein Similarity (ANLS):</b><br>
  $$ANLS = \frac{1}{N} \sum_{i=1}^{N} \max_{g \in G_i} \left( 1 - \frac{NL(g, P_i)}{\max(|g|, |P_i|)} \right)$$
</p>

<p align="center">
  <b>Exact Match (EM):</b><br>
  $$EM = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(P_i \in G_i)$$
</p>

<p align="center">
  <b>F1-Score:</b><br>
  $$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
</p>

<p align="center">
  <b>Cosine Similarity (Semantic Retrieval):</b><br>
  $$\text{sim}(A, B) = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$
</p>

Where:
* $NL(g, P_i)$: Character-level Levenshtein edit distance.
* $G_i$: Set of reference ground-truth variants.
* $P_i$: The model's generated prediction.
* $N$: Total sample size.

## Evaluation Results (DocVQA Benchmark)
The following table summarizes the performance of each perception strategy across accuracy and efficiency dimensions.

| Strategy | ANLS | Exact Match | F1 Score | Latency [s] | Throughput [S/s] | Memory [MB] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hybrid** | **0.24** | **0.20** | **0.30** | 14.2 | 0.07 | 4600 |
| **VLM Standalone** | 0.17 | 0.10 | 0.20 | **4.2** | **0.24** | 4100 |
| **Tesseract** | 0.17 | 0.10 | **0.30** | 11.0 | 0.09 | **350** |
| **PaddleOCR** | 0.13 | 0.00 | 0.10 | 52.3 | 0.02 | 850 |

## Execution
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Setup**:
   Configure `.env` with OpenRouter or local LLM endpoints.
3. **Run Benchmark**:
   ```bash
   python main.py
   ```

## Academic Deliverables
- **Thesis**: `Gold_Submission/Thesis_Diamond_Final.docx`
- **Research Paper**: `Gold_Submission/ArXiv_Paper_Diamond_Final.docx`
- **Presentation**: `Gold_Submission/Final_Defense_Presentation.pptx`

---
*Created by Tifang Desmond Ngoe (2025-2026)*
*Supervised by Prof. Piotr Duda, Czestochowa University of Technology*
