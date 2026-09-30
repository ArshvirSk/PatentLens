"""
Downloads ~5000 REAL US patents from the NortheasternUniversity/big_patent
dataset on HuggingFace (BigPatent corpus) using the `datasets` library.

Each patent has: abstract, description (full text), and CPC class.
The script constructs title and claims from the description text.
"""
import json
import os
import sys
import random
import re

try:
    from datasets import load_dataset
except ImportError:
    print("Please install the datasets library: pip install datasets")
    sys.exit(1)

# CPC section codes to human-readable names
CPC_SECTIONS = {
    "a": {"cpc": "A61B", "name": "Human Necessities"},
    "b": {"cpc": "B60W", "name": "Operations / Transporting"},
    "c": {"cpc": "C07D", "name": "Chemistry / Metallurgy"},
    "d": {"cpc": "D06M", "name": "Textiles / Paper"},
    "e": {"cpc": "E04B", "name": "Fixed Constructions"},
    "f": {"cpc": "F16K", "name": "Mechanical Engineering"},
    "g": {"cpc": "G06F", "name": "Physics / Computing"},
    "h": {"cpc": "H04L", "name": "Electricity / Networking"},
    "y": {"cpc": "Y02E", "name": "Cross-sectional Technology"},
}

DATASET = "NortheasternUniversity/big_patent"

def extract_title_and_claims(description):
    """
    Heuristic: extract a pseudo-title (first sentence) and 
    identify claim-like text from the full description.
    """
    sentences = re.split(r'(?<=[.!?])\s+', description.strip())
    
    # Title = first sentence, capped at 150 chars
    title = sentences[0][:150].strip('.').strip() if sentences else "Untitled"
    
    # Claims = find sections that look like patent claims
    claims_sentences = []
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in ["claim", "comprising", "wherein", "embodiment", "according to"]):
            claims_sentences.append(s)
            if len(claims_sentences) >= 8:
                break
    
    claims = " ".join(claims_sentences) if claims_sentences else " ".join(sentences[1:5])
    return title, claims


def download_patents(total_needed=5000, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    raw_path = os.path.join(output_dir, 'raw', 'patents.json')
    queries_path = os.path.join(output_dir, 'queries', 'evaluation_queries.json')
    
    random.seed(42)
    
    sections = list(CPC_SECTIONS.keys())
    per_section = total_needed // len(sections)
    remainder = total_needed % len(sections)
    
    all_patents = []
    patent_counter = 0
    
    for i, section in enumerate(sections):
        needed = per_section + (1 if i < remainder else 0)
        cpc_info = CPC_SECTIONS[section]
        print(f"Loading dataset for section '{section}' ({cpc_info['name']})...")
        
        try:
            # Load dataset directly via datasets package with streaming to avoid massive downloads
            ds = load_dataset(DATASET, section, split="train", streaming=True) 
            
            section_patents = []
            for row in ds:
                abstract = row.get("abstract", "").strip()
                description = row.get("description", "").strip()
                
                if len(abstract) < 30:
                    continue
                
                title, claims = extract_title_and_claims(description)
                
                patent = {
                    "id": f"US{10000000 + patent_counter}B2",
                    "date": f"20{random.randint(15,24):02d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                    "cpc": cpc_info["cpc"],
                    "assignee": "",
                    "title": title,
                    "abstract": abstract,
                    "claims": claims,
                    "description": description[:3000],  # Cap at 3000 chars to keep index manageable
                    "citations": [],
                }
                section_patents.append(patent)
                patent_counter += 1
                
                if len(section_patents) >= needed:
                    break
                    
            print(f"  Got {len(section_patents)} patents from section '{section}'")
            all_patents.extend(section_patents)
            
        except Exception as e:
            print(f"  Error loading section '{section}': {e}")
    
    # Shuffle and assign cross-section citations
    random.shuffle(all_patents)
    for i, p in enumerate(all_patents):
        num_citations = random.randint(0, min(5, i))
        candidates = list(range(max(0, i - 80), i))
        if candidates:
            same_cpc = [j for j in candidates if all_patents[j]["cpc"] == p["cpc"]]
            diff_cpc = [j for j in candidates if all_patents[j]["cpc"] != p["cpc"]]
            pool = same_cpc * 3 + diff_cpc
            if pool:
                cited = random.sample(pool, min(num_citations, len(pool)))
                p["citations"] = list(set(all_patents[j]["id"] for j in cited))
    
    # Save patents
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(all_patents, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_patents)} real patents -> {raw_path}")
    
    # Generate evaluation queries
    queries = []
    sampled = random.sample(range(len(all_patents)), min(40, len(all_patents)))
    for idx in sampled:
        p = all_patents[idx]
        query_text = " ".join(p["abstract"].split()[:30])
        if len(query_text.strip()) < 15:
            continue
        relevant = [p["id"]] + p.get("citations", [])
        queries.append({
            "query_id": f"Q{idx:04d}",
            "query_text": query_text.strip(),
            "relevant_patents": relevant,
            "source_patent": p["id"],
        })
    
    os.makedirs(os.path.dirname(queries_path), exist_ok=True)
    with open(queries_path, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(queries)} evaluation queries -> {queries_path}")
    print("\nDone! Now run: python scripts/build_index.py")

if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    download_patents(total)
