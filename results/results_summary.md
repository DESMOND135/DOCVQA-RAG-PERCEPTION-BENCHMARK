# DocVQA Pipeline Performance Results Summary

This folder contains the complete output from the Document Visual Question Answering (DocVQA) benchmark run. It includes detailed logs, aggregated metrics, inference samples, and analytical plots comparing four distinct perception mechanisms: Tesseract OCR, PaddleOCR, Vision-Language Models (VLM), and a Hybrid Approach.

---

## 1. Summary of Findings

The evaluation highlights significant trade-offs across four perception approaches in solving spatial reasoning and document analysis tasks:

- **Accuracy:** The **Hybrid** model achieves the highest accuracy across metrics (ANLS, Exact Match, F1), reinforcing that combining pure OCR parsing with the advanced semantic grounding of a Vision-Language Model provides the most robust solution.
- **Latency & Throughput:** **VLM** offers the lowest latency and highest throughput. Deep OCR-based pipelines (like PaddleOCR), while accurate on texts, are severely throttled by sequential text extraction and vector indexing.
- **Memory Overhead:** **Tesseract** operates on a fraction of the memory (under 500MB) compared to deep learning counterparts like PaddleOCR or VLM setups, making it the only feasible choice for highly constrained edge devices.
- **Retrieval Performance:** Retrieving vectors from the database consistently takes very little time, meaning the actual bottleneck of RAG systems applied to Document VQA lies overwhelmingly in the visual processing and text indexing phases.

---

## 2. Graph Explanations

### Accuracy Metrics Comparison (`plots/accuracy_comparison.png`)
- **What is compared:** Overall correctness of answers produced by the four models.
- **Axes:** The X-axis represents the evaluated perception models, while the Y-axis tracks accuracy scale from 0.0 (wrong) to 1.0 (perfect score).
- **Key Observation:** The Hybrid pipeline significantly outperforms all models, overcoming hallucination issues common in VLMs by verifying visual answers against grounded OCR data.

### System Efficiency Analysis (`plots/efficiency_comparison.png`)
- **What is compared:** The computational speed of each pipeline.
- **Axes:** The left bar chart displays processing time per sample (Seconds, Y-axis). The right bar chart displays the throughput rate (Samples processed per second, Y-axis). The X-axis represents the models.
- **Key Observation:** PaddleOCR is drastically slower due to its heavy deep-learning architecture and sequential bounding box extraction, whereas pure VLM sidesteps text detection altogether for much faster inference.

### Peak Memory Usage (`plots/memory_comparison.png`)
- **What is compared:** The maximum memory (RAM/VRAM) required for each perception model during evaluation.
- **Axes:** The X-axis plots the tested perception models; the Y-axis plots Peak Memory Used in Megabytes (MB).
- **Key Observation:** Tesseract is incredibly lightweight. The Hybrid system incurs the highest memory footprint because it must simultaneously load OCR extractors, vector embeddings models, and an LLM engine.

### Database Performance: Indexing vs Retrieval (`plots/database_efficiency.png`)
- **What is compared:** The time spent inserting text vectors versus retrieving answers from the Vector DB.
- **Axes:** X-axis shows the evaluated models, while the Y-axis indicates operation time in seconds.
- **Key Observation:** Indexing (chunking and encoding strings into vector space) is the biggest bottleneck in standard RAG pipelines. Once indexed, retrieval is near-instantaneous for all configurations.
