def precision_at_k(retrieved_docs, relevant_docs, k):
    """
    Computes Precision@K.
    """
    if k == 0:
        return 0.0
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = [doc for doc in retrieved_k if doc in relevant_docs]
    return len(relevant_retrieved) / k

def recall_at_k(retrieved_docs, relevant_docs, k):
    """
    Computes Recall@K.
    """
    if len(relevant_docs) == 0:
        return 0.0
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = [doc for doc in retrieved_k if doc in relevant_docs]
    return len(relevant_retrieved) / len(relevant_docs)

def f1_at_k(retrieved_docs, relevant_docs, k):
    """
    Computes F1-score@K.
    """
    p = precision_at_k(retrieved_docs, relevant_docs, k)
    r = recall_at_k(retrieved_docs, relevant_docs, k)
    if p + r == 0:
        return 0.0
    return 2 * (p * r) / (p + r)

def average_precision(retrieved_docs, relevant_docs):
    """
    Computes Average Precision (AP) for a single query.
    """
    if len(relevant_docs) == 0:
        return 0.0
        
    ap = 0.0
    relevant_count = 0
    
    for i, doc in enumerate(retrieved_docs):
        if doc in relevant_docs:
            relevant_count += 1
            ap += relevant_count / (i + 1)
            
    return ap / len(relevant_docs)

def mean_average_precision(queries_results):
    """
    Computes MAP across multiple queries.
    queries_results: list of tuples (retrieved_docs, relevant_docs)
    """
    if not queries_results:
        return 0.0
        
    map_score = sum(average_precision(ret, rel) for ret, rel in queries_results)
    return map_score / len(queries_results)
