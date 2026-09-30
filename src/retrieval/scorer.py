import math
from collections import defaultdict
from src.retrieval.query_parser import parse_query

class Scorer:
    def __init__(self, indexer):
        self.indexer = indexer
        self.default_weights = {
            'claims': 0.4,
            'title': 0.3,
            'abstract': 0.2,
            'description': 0.1
        }
        
    def score_query(self, query_text, weights=None, top_k=20):
        if weights is None:
            weights = self.default_weights
            
        query_tf = parse_query(query_text)
        
        # doc_scores[doc_id][zone] = score
        doc_scores = defaultdict(lambda: defaultdict(float))
        # explanation[doc_id][zone] = list of matching terms
        explanation = defaultdict(lambda: defaultdict(list))
        
        zones = ['title', 'abstract', 'claims', 'description']
        
        # For each zone, compute Cosine Similarity between Query and all matching Docs
        for zone in zones:
            zone_index = self.indexer.index[zone]
            zone_lengths = self.indexer.doc_lengths[zone]
            
            query_vector_length = 0.0
            
            for term, q_tf in query_tf.items():
                if term in zone_index:
                    postings = zone_index[term]
                    df = len(postings)
                    idf = math.log10(self.indexer.doc_count / (df + 1))
                    
                    q_weight = (1 + math.log10(q_tf)) * idf
                    query_vector_length += q_weight ** 2
                    
                    for doc_id, d_tf in postings.items():
                        d_weight = (1 + math.log10(d_tf)) * idf
                        doc_scores[doc_id][zone] += q_weight * d_weight
                        explanation[doc_id][zone].append(term)
                        
            query_vector_length = math.sqrt(query_vector_length)
            
            # Normalize by lengths
            for doc_id in doc_scores:
                if zone in doc_scores[doc_id] and doc_scores[doc_id][zone] > 0:
                    d_len = zone_lengths.get(doc_id, 1.0) # fallback to 1.0 to avoid div by zero
                    if d_len == 0:
                        d_len = 1.0
                    q_len = query_vector_length if query_vector_length > 0 else 1.0
                    doc_scores[doc_id][zone] = doc_scores[doc_id][zone] / (d_len * q_len)
                    
        # Compute final weighted score
        final_results = []
        for doc_id, z_scores in doc_scores.items():
            final_score = 0.0
            for z in zones:
                final_score += z_scores.get(z, 0.0) * weights.get(z, 0.0)
                
            if final_score > 0:
                metadata = self.indexer.metadata.get(doc_id, {})
                final_results.append({
                    'id': doc_id,
                    'title': metadata.get('title', ''),
                    'date': metadata.get('date', ''),
                    'cpc': metadata.get('cpc', ''),
                    'assignee': metadata.get('assignee', ''),
                    'score': round(final_score, 4),
                    'zone_scores': {z: round(z_scores.get(z, 0.0), 4) for z in zones},
                    'matched_terms': {z: explanation[doc_id][z] for z in zones if z in explanation[doc_id]}
                })
                
        # Sort by final score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results[:top_k]
