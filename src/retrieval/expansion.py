from collections import defaultdict

def expand_query_rocchio(original_query_tf, relevant_docs_tf_list, non_relevant_docs_tf_list, alpha=1.0, beta=0.75, gamma=0.15):
    """
    Rocchio relevance feedback algorithm to adjust query weights.
    
    Args:
    - original_query_tf: dict of term -> weight (TF or TF-IDF) in original query
    - relevant_docs_tf_list: list of dicts, where each dict is term -> weight for a relevant document
    - non_relevant_docs_tf_list: list of dicts, where each dict is term -> weight for a non-relevant document
    - alpha, beta, gamma: Rocchio parameters
    
    Returns:
    - dict of expanded query term -> new weight
    """
    new_query_tf = defaultdict(float)
    
    # 1. Add original query terms
    for term, weight in original_query_tf.items():
        new_query_tf[term] += alpha * weight
        
    # 2. Add relevant document terms
    num_rel = len(relevant_docs_tf_list)
    if num_rel > 0:
        for rel_doc in relevant_docs_tf_list:
            for term, weight in rel_doc.items():
                new_query_tf[term] += (beta / num_rel) * weight
                
    # 3. Subtract non-relevant document terms
    num_non_rel = len(non_relevant_docs_tf_list)
    if num_non_rel > 0:
        for non_rel_doc in non_relevant_docs_tf_list:
            for term, weight in non_rel_doc.items():
                new_query_tf[term] -= (gamma / num_non_rel) * weight
                
    # Keep only terms with positive weights
    final_query = {term: weight for term, weight in new_query_tf.items() if weight > 0}
    return final_query
