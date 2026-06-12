# Systems-Level Reliability and Robustness Evaluation Framework for Document AI
**Master's Thesis Defense**  
Tifang Desmond Ngoe  
Czestochowa University of Technology  
Supervisor: Prof. Piotr Duda  
Academic Year 2025-2026

---

## Introduction / Problem Statement
- **Document AI Complexity**: Modern enterprise pipelines rely heavily on automated extraction of information from complex PDF documents.
- **The PDF Challenge**: Unstructured documents contain rich multi-column formats, dense tabular grids, and geometric layouts that defy simple reading orders.
- **Hallucination & Layout Risks**: Semantic understanding without visual awareness leads to layout-blindness, causing critical extraction failures.
- **Critical Downstream Risk**: A tiny character reading error (e.g., distorting **$1,240.50** into a rounded **$1,200.00** on a scanned invoice) is not just a simple spelling mistake—it propagates into automated financial ledgers, causing catastrophic audit and compliance failures in finance and healthcare.

---

## Data as the Core Foundation of AI
- **The Ultimate Foundation**: Quality data is the absolute catalyst for AI; all downstream reasoning (ML, deep learning, and cognitive LLMs) is fundamentally capped by the accuracy of the perception layer.
- **The Perception Gap**: Enterprise pipelines are saturated with unstructured forms (PDFs and scans) where robust layout understanding and literal character precision are required to unlock factual insights.

---

## Data at the Core of Intelligence
![Data Foundation Infographic](../figures/diagrams/data_foundation_intelligence.jpg)
**Figure 1.0: Data as the Core Foundation of AI Systems**

---

## Research Objective
- **Addressing the Perception-Cognition Gap**: Bridging the disconnect where LLMs show advanced linguistic reasoning but fail at structural, spatial perception.
- **Scientific Goal**: Formulating a rigorous, systems-level reliability evaluation framework for DocVQA architectures under zero-shot conditions.
- **Robustness Benchmarking**: Swapping and analyzing perception modules to establish a reliable accuracy-efficiency frontier for real-world deployments.

---

## Traditional OCR (Tesseract)
- **Heuristic Baseline**: Relies on classical layout algorithms to group and serialize characters.
- **Linearization Fragmentation**: Converts multi-column text horizontally into a single continuous stream, destroying reading order and paragraph alignment.
- **Fidelity Loss**: Separates tabular cells from headers, making spatial relation reasoning impossible.
![OCR Preprocessing](../figures/diagrams/ocr_preprocessing.png)
**Figure 4.3: OCR Preprocessing Pipeline**

---

## PaddleOCR
- **Deep-Learning Spatial Detection**: Employs an academic DBNet detector combined with SVTR recognizer for raw character mapping.
- **Layout Robustness**: Highly precise alphanumeric localization, minimizing character confusion.
- **The Cognitive Limit**: Captures characters perfectly but lacks semantic context, requiring a downstream layout reconstruction layer.
![PaddleOCR Academic](../figures/diagrams/paddleocr_academic.png)
**Figure 2.2: PaddleOCR Advanced Multi-Stage Architecture**

---

## Perception Layer
- **Layout Detection & Text Localization**: Automatically mapping page regions, paragraphs, and nested table cells.
- **Character Grounding**: Indexing absolute 2D bounding boxes $(x_1, y_1, x_2, y_2)$ to ensure alphanumeric fidelity.
- **Spatial Alignment**: Preparing structured, geometry-preserved raw text streams for cognitive processing.
![Layout Detection](../figures/diagrams/layout_detection.png)
**Figure 2.3: Layout Detection and Document Structure Logic**

---

## Vision-Language Models (VLMs)
- **Multimodal Generation**: Treats document images natively as input patches, removing the need for heuristic pipelines.
- **Resolution-Loss Hallucination**: Fixed patch resolutions (e.g., 336x336 pixels) compress fine-grained tabular data, leading to character distortion.
- **The Perception Failure**: "Probabilistic guessing" of dense digits in complex zero-shot layouts due to resolution-loss and pixel alignment errors.
![VLM Limitations](../figures/diagrams/vlm_limitations.png)
**Figure 2.4: VLM Projection Layer and Resolution Constraints**

---

## Hybrid OCR-VLM Synchronization
- **Dual-Stream Synchronization**: Merging the literal precision of PaddleOCR with the high-level semantic layout awareness of VLMs.
- **Perception Safety Net**: Grounding VLM spatial reasonings inside verified deterministic OCR character coordinates.
- **Robustness Fusing**: Drastically reduces layout confusion and generative hallucinations in zero-shot extractions.
![System Architecture](../figures/diagrams/system_architecture.png)
**Figure 4.1: Advanced Global System Orchestration Architecture**

---

## RAG / Connection Layer
- **Vector Space Mapping**: Projecting layout-aware chunked documents into a FAISS vector database using `all-MiniLM-L6-v2`.
- **Hybrid Context Retrieval**: Querying and fetching high-relevance chunks grounded with precise spatial metadata.
- **Cognitive Reasoning**: Supplying localized context to the Mistral 7B Instruct reasoning engine.
![RAG Connection Layer](../figures/diagrams/rag_workflow_academic.png)
**Figure 3.1: Semantic Embedding and Vector Storage Workflow**

---

## Benchmark Framework
- **Test Corpus**: Compiled 50 high-complexity PDFs from the DocVQA validation set (dense nested tables, scan noise, multi-column designs).
- **Strict Zero-Shot Paradigm**: No domain-specific or layout-specific fine-tuning, evaluating raw generalization robustness.
- **Swappable Architecture**: Systematically isolating and measuring the impact of each perception stream under identical reasoning conditions.

---

## ANLS Accuracy Evaluation
- **ANLS Definition**: Standard soft-spelling matching similarity metric for Document Visual QA.
- **N**: Total size of the evaluation corpus (here N = 50 queries).
- **a_i**: Predicted answer string generated by the cognitive model for query i.
- **g_i**: Authoritative human-verified ground truth target answer for query i.
- **s(a_i, g_i)**: Soft similarity score. If similarity is < 0.5, score is 0 to reject hallucinations.
  $$ANLS = \frac{1}{N}\sum_{i=1}^{N} s(a_i,g_i) \quad (3.1)$$

---

## Secondary Performance Metrics
- **Exact Match (EM)**: Strictest binary accuracy requiring character-for-character agreement.
- **F1-Score**: Token-level harmonic mean of Precision P and Recall R measuring lexical overlap.
- **L_i**: System latency (seconds) to process query i through both dual-stream layers.
- **T_p**: System throughput indicating processed query samples per second.
  $$EM = \mathbf{1}(a_i = g_i) \quad (3.2)$$
  $$F1 = 2 \cdot \frac{P \cdot R}{P + R} \quad (3.3)$$
  $$T_p = \frac{N}{\sum L_i} \quad (3.5)$$

---

## Experimental Results
- **Empirical Breakthrough**: The proposed Hybrid model achieves the highest accuracy, outperforming standalone VLMs and OCR pipelines.
- **The Performance Frontier**: Validating that visual layout synchronization is essential to resolve complex DocVQA prompts.
![Accuracy Comparison](../figures/plots/accuracy_comparison.png)
**Figure 7.2: Accuracy Benchmark Matrix (ANLS vs F1)**

---

## Performance Metrics Table
- **Comprehensive Evaluation**: Performance comparison across accuracy, operational latency, throughput, and system resource overhead.
- **Accuracy vs. Efficiency**: The Hybrid model achieves the highest accuracy at the cost of higher latency and RAM consumption.

**Table 7.1: Exhaustive Performance Benchmarking Matrix**
| System Model | ANLS | Exact Match (EM) | F1-Score | Inference Latency | Throughput | RAM Footprint | Search Efficiency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hybrid (Ours)** | **0.24** | **0.20** | **0.30** | **14.20 s** | **0.07 S/s** | **4600 MB** | **Sub-ms (<1ms)** |
| Standalone VLM | 0.17 | 0.10 | 0.20 | 4.20 s | 0.24 S/s | 4100 MB | N/A |
| Tesseract RAG | 0.17 | 0.10 | 0.30 | 11.00 s | 0.09 S/s | 350 MB | Sub-ms (<1ms) |
| PaddleOCR RAG | 0.13 | 0.00 | 0.10 | 52.30 s | 0.02 S/s | 850 MB | Sub-ms (<1ms) |

---

## Ablation Study
- **Isolating Stream Contributions**: Systematic removal of layout spatial detection and character grounding streams.
- **Perception Grounding Efficacy**: Proves that character coordinate anchoring is the primary driver in reducing hallucination rates.

**Table 7.2: Perception Component Ablation Study**
| Architecture | Layout Detection | Text Grounding | VLM Context | ANLS | EM |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hybrid (Full)** | **Yes** | **Yes** | **Yes** | **0.24** | **0.20** |
| No Grounding | Yes | No | Yes | 0.17 | 0.10 |
| No Layout | No | Yes | Yes | 0.13 | 0.00 |

---

## Error Analysis / Case Studies
- **Low ANLS Failure Modes**: Poor document contrast, low scanning resolution, and heavily overlapping text boundaries.
- **Visual Evidence**: VLM resolution-loss vs. Hybrid character-grounding precision.
![Hallucination Comparison](../figures/diagrams/hallucination_comparison.png)
**Figure 7.6: Visual Case Study of VLM Resolution-Loss vs. Hybrid Precision**

---

## Deployment Considerations
- **Accuracy-Efficiency Trade-off**: High-reliability synchronization demands dual neural network overhead (14.2s latency).
- **Memory Footprint**: Fusing multiple streams increases RSS RAM footprint (4600MB).
- **Recommendation**: Deploy in offline mission-critical pipelines, using async processing to mitigate CPU-bound latency.
![Efficiency Comparison](../figures/plots/efficiency_comparison.png)
**Figure 7.3: Accuracy-Efficiency Frontier and Latency Inversion**

---

## Conclusion
- **Bridging the Gap**: Synchronized OCR-VLM architecture successfully bridges the perception-cognition disconnect.
- **Grounding Efficacy**: Deterministic character grounding is vital for eliminating LLM hallucinations in structured documents.
- **Standardized Framework**: Provides a repeatable system-level benchmark for modern Document AI research.

---

## Future Work: Multi-Agent System
- **Agentic Pipeline Evolution**: Transitioning from a rigid pipeline to a cooperative multi-agent network.
- **Layout Detection Agent**: Responsible for spatial column splits, tabular boundary parsing, and geometric structure.
- **Text Detection & OCR Agent**: Specialized in high-fidelity character recognition, raw transcription, and bounding box coordinates.
- **Image & Visual Perception Agent**: Dedicated to understanding non-textual primitives, charts, figures, and embedded artwork.
- **Coordinator & Routing Agent**: Orchestrating agent dialogue, resolving data conflicts, and synthesizing unified factual contexts.

---

# Thank You
**Thank You for Your Attention**  
Questions & Discussion  
Tifang Desmond Ngoe  
Academic Year 2025-2026
