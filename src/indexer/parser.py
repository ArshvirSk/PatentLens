import json
import os

def load_patents(filepath):
    """
    Loads patent documents from a JSON file.
    Returns a list of dictionary objects.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
