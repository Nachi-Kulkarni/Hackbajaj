<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Evaluating RAG Systems: Metrics for Accuracy and Hallucination Detection

Evaluating RAG (Retrieval-Augmented Generation) systems requires a **multi-dimensional approach** that goes beyond traditional ML metrics like F1 score. Since RAG combines both retrieval and generation components, you need to assess both phases while specifically targeting hallucination detection.

## Key Metrics for Non-Hallucinatory RAG Evaluation

### **Faithfulness - The Primary Hallucination Detector**

**Faithfulness** is the closest equivalent to F1 score for RAG hallucination detection[^1]. This metric measures **the fraction of claims in the answer that are supported by the provided context**[^1]. It directly addresses your concern about non-hallucinatory outputs by quantifying how well the generated response sticks to the retrieved information.

### **RAGAS Framework Metrics**

The RAGAS (RAG Assessment) framework provides the most comprehensive evaluation suite specifically designed for RAG systems[^2][^1]:

- **Faithfulness**: Measures factual accuracy against retrieved context
- **Answer Relevancy**: Evaluates semantic similarity between the original question and LLM-generated questions from the answer[^1]
- **Context Recall**: Assesses whether relevant context is included in the generated output[^3]
- **Context Precision**: Checks if only relevant and valuable context is being used[^3]


## F1 Score Equivalents for RAG

### **Token-Level F1 Score**

You can still use **F1 score at the token level** for RAG evaluation[^4]. This approach:

- Compares token overlap between generated response and ground truth
- Calculates precision (how much generated text is correct) and recall (how much correct answer is included)
- Combines them into F1: `F1 = 2 × (Precision × Recall) / (Precision + Recall)`[^4]

**Example calculation**[^4]:

- Ground truth: "He eats an apple" → Tokens: [he, eats, an, apple]
- Generated: "He ate an apple" → Tokens: [he, ate, an, apple]
- True positives: 3, False positives: 1, False negatives: 1
- Precision = 3/4 = 0.75, Recall = 3/4 = 0.75, **F1 = 0.75**


### **Retrieval-Specific F1 Applications**

**Mean Average Precision (MAP)** and **F1 score serve different purposes**[^5]:

- **MAP**: Ideal when document ranking order matters (e.g., top-3 results fed to generator)
- **F1 Score**: Better when you need to balance precision and recall equally, less sensitive to ranking[^5]


## Comprehensive Evaluation Approach

### **Two-Phase Evaluation Strategy**

**Best practice is to evaluate retrieval and generation components separately**[^3]:

**Retrieval Phase Metrics**:

- **Precision@k**: Fraction of top-k retrieved documents that are relevant
- **Recall@k**: Fraction of all relevant documents found in top-k results[^3]
- **NDCG (Normalized Discounted Cumulative Gain)**: Measures ranking quality[^3]

**Generation Phase Metrics**:

- **BLEU/ROUGE**: Text similarity to reference answers
- **Coherence**: Logical flow and readability of generated text[^6]
- **Contextual Relevancy**: How well retrieved documents contribute to the answer[^3]


### **Hallucination Detection Methods**

Recent benchmarking shows **multiple approaches for detecting hallucinations**[^1]:

1. **RAGAS Faithfulness**: Most effective for simple search-like queries
2. **Self-Evaluation (LLM-as-a-judge)**: LLM rates its own confidence on 1-5 scale
3. **Trustworthy Language Model (TLM)**: Consistently outperforms other methods across benchmarks[^1]

## Practical Implementation Guidelines

### **Threshold Recommendations**

For production RAG systems[^7]:

- **F1 Score**: 85% or higher indicates good balance between precision and recall
- **Faithfulness**: Aim for >90% to minimize hallucinations
- **Answer Relevancy**: Target >80% semantic similarity


### **Custom Metric Development**

You can create **domain-specific rubric-based metrics**[^8] using frameworks like RAGAS:

```
Score 1: No hallucination - all information present in context
Score 2: No factual errors but lacks important details  
Score 3: Many statements not present in context
Score 4: Contains factual errors and lacks details
Score 5: Contradicts retrieved context
```


## Recommended Evaluation Workflow

1. **Start with RAGAS Faithfulness** as your primary hallucination detector
2. **Complement with traditional metrics** like F1 score at token level for accuracy
3. **Use MAP or NDCG** for retrieval quality assessment
4. **Implement contextual metrics** (Context Recall/Precision) for comprehensive evaluation
5. **Consider LLM-as-a-judge** for nuanced quality assessment

The key insight is that **RAG evaluation requires multiple metrics working together** rather than a single F1-equivalent. Faithfulness serves as your primary anti-hallucination metric, while F1 score and retrieval metrics provide complementary accuracy assessments for a complete evaluation framework.

<div style="text-align: center">⁂</div>

[^1]: https://cleanlab.ai/blog/rag-tlm-hallucination-benchmarking/

[^2]: https://cloud.google.com/blog/products/ai-machine-learning/optimizing-rag-retrieval

[^3]: https://orq.ai/blog/rag-evaluation

[^4]: https://neptune.ai/blog/evaluating-rag-pipelines

[^5]: https://zilliz.com/ai-faq/how-can-mean-average-precision-map-or-f1score-be-used-in-evaluating-retrieval-results-for-rag-and-in-what-scenarios-would-these-be-insightful

[^6]: https://www.datategy.net/2024/09/27/how-to-measure-rag-from-accuracy-to-relevance/

[^7]: https://www.linkedin.com/pulse/guide-metrics-thresholds-evaluating-rag-llm-models-kevin-amrelle-dswje

[^8]: https://docs.ragas.io/en/stable/howtos/customizations/metrics/_write_your_own_metric/

[^9]: https://www.pinecone.io/learn/series/vector-databases-in-production-for-busy-engineers/rag-evaluation/

[^10]: https://huggingface.co/learn/cookbook/en/rag_evaluation

[^11]: https://myscale.com/blog/ultimate-guide-to-evaluate-rag-system/

[^12]: https://arize.com/blog-course/f1-score/

[^13]: https://docs.datastax.com/en/ragstack/intro-to-rag/evaluating.html

[^14]: https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more

[^15]: https://www.baeldung.com/cs/retrieval-augmented-generation-evaluate-metrics-performance

[^16]: https://towardsdatascience.com/benchmarking-hallucination-detection-methods-in-rag-6a03c555f063/

[^17]: https://www.protecto.ai/blog/understanding-llm-evaluation-metrics-for-better-rag-performance/

[^18]: https://www.elastic.co/search-labs/blog/evaluating-rag-metrics

[^19]: https://machinelearningmastery.com/rag-hallucination-detection-techniques/

[^20]: https://qdrant.tech/blog/rag-evaluation-guide/

