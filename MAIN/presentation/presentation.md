# Systems-Level Reliability and Robustness Evaluation Framework for Document AI
**Master's Thesis Defense**  
Tifang Desmond Ngoe  
Czestochowa University of Technology  
Supervisor: Prof. Piotr Duda  
Academic Year 2025-2026

---

## The Document AI Challenge
- **Enterprise Bottleneck**: Modern pipelines rely heavily on extracting unstructured data from complex PDFs.
- **Visual Complexity**: Dense tabular grids and multi-column geometries defy simple text reading orders.
- **The Perception Gap**: Semantic LLMs without spatial awareness hallucinate structural data.
- **Critical Risk**: A minor layout misread (e.g., distorting $1,240.50) triggers catastrophic failures in downstream financial audits.

---

## Data as the Core Foundation of AI
- **The Ultimate Catalyst**: All downstream cognitive reasoning is fundamentally capped by the accuracy of the perception layer.
- **Bridging the Disconnect**: We must bridge the gap where LLMs show advanced linguistic reasoning but fail at structural, spatial perception.
![Data Foundation Infographic](../figures/diagrams/data_foundation_intelligence.jpg)
**Figure 1.0: Data as the Core Foundation of AI Systems**

---

## Research Objective
- **Formulate a Benchmark**: Create a rigorous reliability evaluation framework for DocVQA architectures under zero-shot conditions.
- **Investigate Perception**: Isolate and evaluate the exact impact of spatial grounding on LLM hallucination rates.
- **Establish a Frontier**: Map the accuracy-efficiency trade-offs across Traditional OCR, VLMs, and Hybrid models.

---

## Traditional Baseline: OCR (Tesseract)
- **Heuristic Algorithms**: Relies on rigid rules to group characters.
- **Linearization Failure**: Converts multi-column layouts into a single, corrupted horizontal text stream.
- **Fidelity Loss**: Completely destroys spatial relationships inside complex tables.
![OCR Preprocessing](../figures/diagrams/ocr_preprocessing.png)
**Figure 4.3: OCR Preprocessing Pipeline**

---

## Modern Baseline: Vision-Language Models (VLMs)
- **Multimodal Promising**: Treats entire document images natively as input patches.
- **Resolution Constraints**: Fixed patch limits (e.g., 336x336 pixels) heavily compress dense tabular data.
- **The Perception Failure**: Zero-shot VLMs probabilistically "guess" digits when pixel alignment is lost, leading to severe hallucination.
![VLM Limitations](../figures/diagrams/vlm_limitations.png)
**Figure 2.4: VLM Projection Layer and Resolution Constraints**

---

## Proposed Solution: Hybrid OCR-VLM
- **Dual-Stream Synchronization**: Merges the literal character precision of PaddleOCR with the semantic layout awareness of VLMs.
- **Spatial Anchoring**: Indexes exact 2D bounding boxes $(x_1, y_1, x_2, y_2)$ for absolute alphanumeric fidelity.
- **Perception Safety Net**: Grounds VLM reasoning inside verified, deterministic OCR coordinates to eliminate hallucination.
![System Architecture](../figures/diagrams/system_architecture.png)
**Figure 4.1: Advanced Global System Orchestration Architecture**

---

## RAG Connection Layer
- **Vector Space Mapping**: Layout-aware documents are chunked and projected into a FAISS database using `all-MiniLM-L6-v2`.
- **Hybrid Retrieval**: Fetches high-relevance chunks mathematically grounded with precise spatial metadata.
- **Cognitive Reasoning**: Feeds deterministic context directly into the Mistral 7B Instruct reasoning engine.
![RAG Connection Layer](../figures/diagrams/rag_workflow_academic.png)
**Figure 3.1: Semantic Embedding and Vector Storage Workflow**

---

## Evaluation Benchmark & Metrics
- **Test Corpus**: 50 high-complexity zero-shot PDFs from the DocVQA validation set (dense tables, scans, multi-columns).
- **ANLS (Soft Similarity)**: Penalizes hallucinations while allowing minor formatting variances.
  $$ANLS = \frac{1}{N}\sum_{i=1}^{N} s(a_i,g_i) \quad (3.1)$$
- **Exact Match (EM)**: Strictest binary accuracy.
  $$EM = \mathbf{1}(a_i = g_i) \quad (3.2)$$
- **F1-Score**: Token-level lexical overlap measuring precision and recall.

---

## Experimental Results
- **Empirical Breakthrough**: The Hybrid model strictly outperforms standalone VLMs and Traditional OCR.
- **Visual Evidence**: Synchronization successfully prevents layout-blindness.
![Accuracy Comparison](../figures/plots/accuracy_comparison.png)
**Figure 7.2: Accuracy Benchmark Matrix (ANLS vs F1)**

---

## Key Performance Findings
- **Massive Improvement**: The Hybrid model achieves a **41% improvement** in ANLS accuracy over standalone VLMs (0.17 $\rightarrow$ 0.24).
- **Trade-off**: Superior accuracy requires significantly higher latency (14.2s) and RAM footprint (4.6GB) due to dual-stream processing.

**Table 7.1: Exhaustive Performance Benchmarking Matrix**
| System Model | ANLS | Exact Match (EM) | F1-Score | Inference Latency | Throughput | RAM Footprint | Search Efficiency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hybrid (Ours)** | **0.24** | **0.20** | **0.30** | **14.20 s** | **0.07 S/s** | **4600 MB** | **Sub-ms (<1ms)** |
| Standalone VLM | 0.17 | 0.10 | 0.20 | 4.20 s | 0.24 S/s | 4100 MB | N/A |
| Tesseract RAG | 0.17 | 0.10 | 0.30 | 11.00 s | 0.09 S/s | 350 MB | Sub-ms (<1ms) |
| PaddleOCR RAG | 0.13 | 0.00 | 0.10 | 52.30 s | 0.02 S/s | 850 MB | Sub-ms (<1ms) |

---

## Ablation Study: Why it Works
- **Isolating Variables**: We systematically removed the layout parsing and character grounding layers.
- **The Core Finding**: Removing deterministic character grounding collapses Exact Match accuracy back to zero.

**Table 7.2: Perception Component Ablation Study**
| Architecture | Layout Detection | Text Grounding | VLM Context | ANLS | EM |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hybrid (Full)** | **Yes** | **Yes** | **Yes** | **0.24** | **0.20** |
| No Grounding | Yes | No | Yes | 0.17 | 0.10 |
| No Layout | No | Yes | Yes | 0.13 | 0.00 |

---

## Error Analysis & Visual Evidence
- **VLM Failure Mode**: Guessing digits incorrectly due to low patch resolution.
- **Hybrid Precision**: Anchoring logic preserves exact numerical strings.
![Hallucination Comparison](../figures/diagrams/hallucination_comparison.png)
**Figure 7.6: Visual Case Study of VLM Resolution-Loss vs. Hybrid Precision**

---

## Conclusion
- **Bridging the Gap**: Synchronized OCR-VLM architecture successfully bridges the perception-cognition disconnect.
- **Grounding Efficacy**: Deterministic character grounding is vital for eliminating LLM hallucinations in structured enterprise documents.
- **Standardized Framework**: Provides a repeatable, zero-shot system-level benchmark for future Document AI research.

---

## Future Work: Multi-Agent System
- **Evolution**: Transitioning from a rigid linear pipeline to a cooperative multi-agent network.
- **Agent Roles**:
  - **Layout Agent**: Parses boundaries and geometric structures.
  - **OCR Agent**: High-fidelity character transcription.
  - **Visual Agent**: Processes embedded charts and figures.
  - **Coordinator Agent**: Resolves spatial conflicts and synthesizes the final factual answer.

---

# Thank You
**Thank You for Your Attention**  
Questions & Discussion  
Tifang Desmond Ngoe  
Academic Year 2025-2026
