# EVALUATION.md

## Purpose
This document defines how to test whether Campus Genius is working correctly and whether it is useful for Tamil-English academic document question answering.

## Evaluation Goals
- Check if retrieved chunks are relevant.
- Check if answers are grounded in document content.
- Check if citations match the source.
- Check if Tamil, English, and mixed-language queries work well.
- Check if viva questions are meaningful and document-based.

## Evaluation Datasets
Create a small but representative test set with:
- Tamil-only questions.
- English-only questions.
- Mixed Tamil-English questions.
- Short factual questions.
- Conceptual questions.
- Questions that require page-specific retrieval.
- Questions whose answers are not present in the document.

## Test Categories
### Retrieval Tests
Measure whether the top retrieved chunks actually contain the answer.

### Answer Quality Tests
Check whether the generated response:
- answers the question correctly,
- stays within the document context,
- avoids hallucination,
- uses the right language.

### Citation Tests
Check whether:
- citations point to the correct chunk or page,
- citations are included when required,
- unsupported answers are clearly marked.

### Viva Question Tests
Check whether generated viva questions:
- are relevant to the document,
- match the topic,
- vary in difficulty,
- are understandable for students.

## Suggested Metrics
### Retrieval
- Top-k relevance.
- Recall@k.
- Exact answer hit rate.

### Generation
- Correctness.
- Groundedness.
- Language match.
- Hallucination rate.

### Citations
- Citation presence rate.
- Citation correctness rate.

### Viva Output
- Topic relevance.
- Difficulty balance.
- Clarity.

## Manual Review Checklist
For each test case, verify:
- The question is understood correctly.
- The retrieved chunks are relevant.
- The answer uses only retrieved context.
- The answer language is appropriate.
- The citations match the content.
- The system says "not found" when needed.

## Failure Cases To Record
- Wrong chunk retrieved.
- Answer invented beyond the document.
- Wrong language output.
- Missing citation.
- Poor handling of mixed-language query.
- Failure on scanned or noisy PDF.
- Failure on long documents.

## Sample Test Template
```md
- Document:
- Page:
- Query:
- Expected answer:
- Retrieved chunk(s):
- Generated answer:
- Citation correct?:
- Pass/Fail:
- Notes:
```

## Baseline Comparison
If possible, compare the system against:
- English-only embedding retrieval.
- Plain keyword search.
- No-context generation.

This helps prove whether multilingual retrieval improves results.

## Acceptance Criteria
The system is acceptable if:
- it retrieves relevant chunks for most test queries,
- answers are grounded in the uploaded document,
- citations are present and correct,
- Tamil and mixed-language queries work reasonably well,
- viva questions are document-specific and useful.

## Final Review
Before submission, run the evaluation set on:
- at least one English academic PDF,
- at least one Tamil academic PDF,
- at least one mixed-language document,
- at least one scanned or difficult PDF if available.

## Output Of Evaluation
Store:
- test questions,
- retrieved chunks,
- model answers,
- manual scores,
- failure notes,
- final summary.