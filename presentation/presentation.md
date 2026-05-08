# Systems-Level Reliability and Robustness Evaluation Framework for Document AI
**Master's Thesis Defense**  
Bridging the Perception-Cognition Gap in Multimodal Reasoning  
Academic Year 2025-2026

---

## The Motivation: High-Risk Document AI
- **The Challenge**: Mission-critical sectors (Finance, Healthcare) require exact precision from unstructured PDFs.
- **The Bottleneck**: Standalone Large Language Models (LLMs) are linguistically robust but lack spatial awareness.
- **The Perception-Cognition Gap**: A disconnect between a model's reasoning and its ability to "see" fine-grained textual evidence.
- **The Cost of Failure**: Hallucination-related errors in automated pipelines.

---

## The Research Gap: Heuristics vs. Generative
- **Traditional OCR (Tesseract)**: Preserves literal characters but linearizes text horizontally, causing **Structural Fragmentation**.
- **Standalone VLMs (Gemini, LLaVA)**: Elegant multimodal perception but limited by **Resolution-Loss Hallucination**.
- **The Missing Link**: Lack of benchmarking evaluating the trade-offs between deterministic parsing and semantic layout mapping.

---

## Proposed Solution: Hybrid Dual-Stream Synchronization
- **Core Strategy**: Simultaneously process two independent data streams:
  - **Stream 1 (Deterministic)**: PaddleOCR for high-precision character detection.
  - **Stream 2 (Semantic)**: Vision-Language Model for layout context.
- **Grounding Reliability**: Grounding visual summaries in OCR character sequences to suppress resolution-loss errors.

---

## System Architecture: Modular Evaluation Pipeline
![System Architecture](../figures/diagrams/system_architecture.png)

---

## Layout-Aware Retrieval Strategy
- **Dual-Stream Logic**: Fusing character tokens and spatial embeddings in a shared vector space (FAISS).
- **Zero-Shot Protocol**: Evaluating robustness without task-specific fine-tuning.

---

## Mathematical Formalization of Reliability
- **Hybrid Synchronization**: $C = S_{ocr} \parallel S_{vlm}$
- **Accuracy Metric: ANLS**:
  $$ANLS = \frac{1}{N}\sum_{i=1}^{N} s(a_i,g_i)$$
- **Fidelity Metric: Exact Match**: Binary indicator of absolute precision.

---

## The Accuracy-Efficiency Frontier
![Accuracy Tradeoff](../figures/plots/accuracy_tradeoff.png)

---

## Benchmarking Results: Performance Delta
- **Observation**: The Hybrid model achieves significantly higher ANLS scores over standalone VLMs in dense tabular environments.
- **Trade-off**: Improving perception fidelity requires a significant computational trade-off in inference latency.

---

## Quantitative Evidence: Efficiency & Memory
![Efficiency Comparison](../figures/plots/efficiency_comparison.png)

---

## Resource Footprint Analysis
- **Throughput Inversion**: While VLMs provide higher throughput, their reliability in zero-shot extractions is significantly lower.
- **Memory Consumption**: Hybrid models demand higher memory (RSS) due to dual-stream synchronization overhead.

---

## Visualizing Failure Modes: Hallucination Case Study
![Hallucination Comparison](../figures/diagrams/hallucination_comparison.png)

---

## Qualitative Analysis: Standalone VLM vs Hybrid
- **VLM Failure**: Resolution-loss causes rounding errors and "probabilistic guessing" in financial figures.
- **Hybrid Remediation**: Deterministic OCR grounding recovers exact alphanumeric sequences ($1,240.50$ vs $1,200.00$).

---

## Discussion: Structural Robustness & Limitations
- **Adversarial Complexity**: Low ANLS scores reflect the benchmark's focus on high-complexity, multi-column adversarial layouts.
- **Computational Overhead**: Dual-stream synchronization increases latency, necessitating future GPU-accelerated optimization.

---

## Conclusion and Future Directions
- **Conclusion**: Fusing character grounding with semantic layout awareness is essential for mitigating hallucinations in mission-critical AI.
- **Future Work**: Scaling across dense tabular corpora and Investigating natively layout-aware architectures (LayoutLMv3).

---

# Thank You
**Questions & Discussion**  
Systems-Level Reliability Evaluation of Multimodal Document AI
