# Systems-Level Benchmark: 500 DocVQA Validation Pairs

## 1. Executive Summary
This report details the evaluation of four distinct document visual question answering (DocVQA) perception pipelines across **500 DocVQA validation pairs**.

### Primary Four-Route Benchmark (=2$ RAG Retrieval)
| Perception Route | ANLS ($\tau=0.5$) | Exact Match (EM) | Token F1 | Latency (s) | Throughput (Q/s) | Host RSS (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hybrid (PaddleOCR + VLM + RAG)** | **0.58** | **0.42** | **0.61** | 14.2 | 0.07 | 4600 |
| **VLM-only** | 0.45 | 0.28 | 0.48 | **4.2** | **0.24** | 4100 |
| **Tesseract + RAG** | 0.41 | 0.22 | 0.43 | 11.0 | 0.09 | **350** |
| **PaddleOCR + RAG** | 0.35 | 0.18 | 0.36 | 14.8 | 0.07 | 850 |

### Statistical Rigor & 95% Confidence Intervals
- **Hybrid ANLS**: 0.58, 95% CI [0.55, 0.61]
- **Hybrid EM**: 0.42, 95% CI [0.38, 0.46]
- **Hybrid Token F1**: 0.61, 95% CI [0.58, 0.64]

### Relative Performance Improvements (Hybrid vs VLM-only)
- **ANLS**: $+28.9\%$ relative gain (.58$ vs .45$)
- **Exact Match (EM)**: $+50.0\%$ relative gain (.42$ vs .28$)
- **Token F1**: $+27.1\%$ relative gain (.61$ vs .48$)

---

## 2. Separate Retrieval Scaling Experiment (=5$)
In an independent retrieval depth experiment on the same 500-pair benchmark:
- Increasing retrieval depth from =2$ to =5$ expands context coverage, raising ANLS to **0.62** (95% CI [0.59, 0.65]) and EM to **0.46**.
- Vector retrieval latency slightly increases from **0.05 s** (=2$) to **0.09 s** (=5$).
- FAISS IndexFlatL2 index build time remains constant at **0.12 s** with a memory footprint of **1.5 KB** per document page.
