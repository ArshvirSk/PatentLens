from src.indexer.preprocess import preprocess_text
from collections import defaultdict

def parse_query(query_text):
    """
    Parses a free-text query and returns a dictionary of term frequencies.
    """
    tokens = preprocess_text(query_text)
    
    tf = defaultdict(int)
    for token in tokens:
        tf[token] += 1
        
    return tf
