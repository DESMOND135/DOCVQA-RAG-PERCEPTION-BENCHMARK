# Error Analysis Report: DocVQA Perception Strategies

This report provides a systematic analysis of the errors observed across the four perception strategies (Tesseract, PaddleOCR, VLM, and Hybrid) in the DocVQA RAG pipeline.

## Error Categorization

Based on a qualitative review of the predictions compared to the ground truth, the failures fall into four primary categories:

### 1. OCR Misinterpretation (Alphanumeric Confusion)
*   **Description**: The OCR engine correctly identifies that text exists but misreads specific characters.
*   **Examples**: 
    *   Reading "0" (zero) as "O" (capital letter).
    *   Reading "1" (one) as "l" (lowercase L).
    *   Misidentifying currency symbols (e.g., "$" as "S" or "8").
*   **Impact**: This primarily affects **Exact Match (EM)** scores, as even a single character error results in a score of zero, while ANLS remains relatively high.

### 2. Layout Fragmentation and Column Reading
*   **Description**: The perception layer fails to recognize the visual structure of the document, leading to incorrect reading orders.
*   **Examples**: 
    *   In multi-column research papers, the OCR may read straight across columns instead of down one column and up the next.
    *   Complex tables being flattened into a single string of text, losing the relationship between headers and values.
*   **Impact**: Significantly degrades **Retrieval** accuracy, as the text chunks stored in the vector database contain fragmented and nonsensical information.

### 3. Retrieval Ambiguity in Dense Documents
*   **Description**: The RAG system retrieves a text chunk that contains the correct *label* but the incorrect *value* when multiple similar fields exist.
*   **Examples**: 
    *   An invoice with multiple "Total" fields (Subtotal, Tax Total, Grand Total). The retriever may pull the "Tax Total" chunk instead of the requested "Grand Total".
*   **Impact**: Leads to highly confident but incorrect predictions from the LLM.

### 4. Output Formatting and Normalization
*   **Description**: The model extracts the correct information but presents it in a format that differs from the ground truth.
*   **Examples**: 
    *   Ground Truth: `['$1,000']`
    *   Prediction: `1,000 dollars` or `1000`
*   **Impact**: Decreases both ANLS and F1 scores despite the system successfully "finding" the answer.

## Model-Specific Observations

| Error Type | Tesseract | PaddleOCR | VLM | Hybrid |
| :--- | :---: | :---: | :---: | :---: |
| Alphanumeric Misread | High | Medium | Low | Low |
| Layout Fragmentation | High | Medium | Low | Low |
| Scaling Issues | Low | High | Low | Medium |
| Narrative Filler | Low | Low | Medium | Medium |

## Mitigation Strategies
To improve future iterations of this pipeline, it is recommended to:
1.  **Implement OCR Post-Processing**: Use a spell-checker or LLM-based refiner to fix common alphanumeric substitutions.
2.  **Increase Retrieval top-k**: Allow the retriever to provide more context chunks to the LLM to provide better disambiguation for dense documents.
3.  **Strict Normalization**: Apply aggressive text normalization (removing currency, lowercase, removing punctuation) to both Ground Truth and Prediction before metric calculation.
