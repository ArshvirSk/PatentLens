import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indexer.parser import load_patents
from src.indexer.index_builder import InvertedIndex

def main():
    raw_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'patents.json')
    index_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'inverted_index.json')
    
    print(f"Loading raw patents from {raw_path}...")
    patents = load_patents(raw_path)
    
    print(f"Loaded {len(patents)} patents. Building index...")
    indexer = InvertedIndex()
    for i, patent in enumerate(patents):
        indexer.add_document(patent)
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} documents...")
            
    print("Computing TF-IDF lengths...")
    indexer.compute_tfidf_lengths()
    
    print(f"Saving inverted index to {index_path}...")
    indexer.save(index_path)
    print("Done!")

if __name__ == "__main__":
    main()
