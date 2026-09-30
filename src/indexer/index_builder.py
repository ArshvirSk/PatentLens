import json
import os
import math
from collections import defaultdict
from src.indexer.preprocess import preprocess_text

class InvertedIndex:
    def __init__(self):
        # index[zone][term] = {doc_id: term_frequency}
        self.index = {
            'title': defaultdict(lambda: defaultdict(int)),
            'abstract': defaultdict(lambda: defaultdict(int)),
            'claims': defaultdict(lambda: defaultdict(int)),
            'description': defaultdict(lambda: defaultdict(int))
        }
        # doc_lengths[zone][doc_id] = length (used for cosine similarity normalization later)
        self.doc_lengths = {
            'title': defaultdict(float),
            'abstract': defaultdict(float),
            'claims': defaultdict(float),
            'description': defaultdict(float)
        }
        # Document count for IDF
        self.doc_count = 0
        # Store metadata for quick retrieval
        self.metadata = {}

    def add_document(self, patent):
        doc_id = patent['id']
        self.metadata[doc_id] = {
            'date': patent.get('date', ''),
            'cpc': patent.get('cpc', ''),
            'title': patent.get('title', ''),
            'abstract': patent.get('abstract', ''),
            'assignee': patent.get('assignee', ''),
            'citations': patent.get('citations', []),
        }
        self.doc_count += 1
        
        zones = ['title', 'abstract', 'claims', 'description']
        for zone in zones:
            text = patent.get(zone, "")
            tokens = preprocess_text(text)
            
            # Calculate term frequencies
            tf = defaultdict(int)
            for token in tokens:
                tf[token] += 1
                
            # Add to index
            for token, count in tf.items():
                self.index[zone][token][doc_id] = count

    def compute_tfidf_lengths(self):
        """
        Precompute document lengths for cosine similarity normalization.
        Vector length = sqrt(sum((TF * IDF)^2)) for a document in a zone.
        """
        for zone, zone_index in self.index.items():
            for term, postings in zone_index.items():
                # df is the number of docs containing this term in this zone
                df = len(postings)
                idf = math.log10(self.doc_count / (df + 1)) # Add 1 to avoid div by zero
                
                for doc_id, tf in postings.items():
                    # Standard TF-IDF weight: (1 + log10(tf)) * idf
                    weight = (1 + math.log10(tf)) * idf
                    self.doc_lengths[zone][doc_id] += weight ** 2
                    
        # sqrt for final lengths
        for zone in self.doc_lengths:
            for doc_id in self.doc_lengths[zone]:
                self.doc_lengths[zone][doc_id] = math.sqrt(self.doc_lengths[zone][doc_id])

    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Convert defaultdicts to regular dicts for JSON serialization
        save_data = {
            'index': {z: {t: dict(p) for t, p in self.index[z].items()} for z in self.index},
            'doc_lengths': {z: dict(dl) for z, dl in self.doc_lengths.items()},
            'doc_count': self.doc_count,
            'metadata': self.metadata
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f)
            
    def load(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        self.index = save_data['index']
        self.doc_lengths = save_data['doc_lengths']
        self.doc_count = save_data['doc_count']
        self.metadata = save_data['metadata']

