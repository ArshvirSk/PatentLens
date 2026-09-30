# PatentLens — Prior-Art Search Engine

PatentLens is a full-featured Information Retrieval (IR) system built for searching through patent documents. Designed for the CSDC7023 syllabus, it features a custom Python-based inverted index, TF-IDF weighting, Cosine Similarity scoring, and an interactive evaluation dashboard, all wrapped in a premium dark-themed SPA (Single Page Application).

It is powered by a real-world dataset of 5,000 US Patents sourced from the HuggingFace BigPatent corpus.

---

## 🚀 Key Features

* **Custom Inverted Index:** Built from scratch in Python to process documents into a term-document matrix without external search libraries (like Elasticsearch).
* **Multi-Zone Scoring:** Searches across `title`, `abstract`, `claims`, and `description` zones. Users can adjust zone weights dynamically in the UI.
* **TF-IDF & Cosine Similarity:** Employs precise Vector Space Model (VSM) calculations to rank the most relevant documents.
* **Evaluation Harness:** Includes 40 labeled queries with citation-based ground truth to calculate standard IR metrics: **MAP**, **Precision@K**, **Recall@K**, and **F1@K**.
* **Premium UI:** A sleek, dark-themed interface built with vanilla CSS and JS, featuring a real-time search interface, metrics dashboard, index explorer, and an interactive "How It Works" guide.

---

## 📂 Project Structure

```text
PatentLens/
├── data/
│   ├── raw/patents.json                # 5,000 REAL US Patents (BigPatent dataset)
│   ├── processed/inverted_index.json   # Per-zone inverted index + precomputed TF-IDF
│   └── queries/evaluation_queries.json # 40 labeled evaluation queries
├── scripts/
│   ├── download_real_patents.py        # HuggingFace Datasets streaming download script
│   ├── generate_dummy_patents.py       # Fallback synthetic patent generator
│   └── build_index.py                  # Parses raw JSON and builds the inverted index
├── src/
│   ├── api/
│   │   └── app.py                      # Flask API (endpoints for search, stats, eval)
│   ├── evaluation/
│   │   └── metrics.py                  # Evaluation formulas (MAP, P@K, R@K, F1@K)
│   ├── indexer/
│   │   ├── parser.py                   # Document tokenizer and stemmer
│   │   ├── preprocess.py               # Stopword removal and Porter Stemming
│   │   └── index_builder.py            # Core inverted index construction logic
│   ├── retrieval/
│   │   ├── query_parser.py             # Parses queries to match index structure
│   │   ├── scorer.py                   # VSM scoring and weighted zone calculation
│   │   └── expansion.py                # Placeholder for Rocchio Relevance Feedback
│   └── ui/
│       ├── index.html                  # Multi-tab Single Page Application
│       ├── styles.css                  # UI styling and CSS variables
│       └── app.js                      # Application logic and API integration
├── requirements.txt                    # Python dependencies
└── README.md                           # You are here!
```

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ArshvirSk/All-Semester-6-Mini-Projects.git
   cd "All-Semester-6-Mini-Projects/IR/PatentLens"
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Re-download data and build the index:**
   *Note: The dataset and inverted index are already included in the `data/` folder, but you can regenerate them if needed.*
   ```bash
   # Downloads 5,000 patents (requires datasets library)
   python scripts/download_real_patents.py 5000 
   
   # Builds the inverted_index.json
   python scripts/build_index.py
   ```

5. **Start the API & UI Server:**
   ```bash
   python src/api/app.py
   ```

6. **Access the application:**
   Open your browser and navigate to [http://localhost:5000](http://localhost:5000)

---

## 🧠 IR Concepts Mapped to Syllabus

PatentLens serves as an educational implementation of core Information Retrieval concepts:

1. **Boolean Retrieval & Tokenization** (Module 1): Handled in `src/indexer/preprocess.py` using regex and NLTK for stopword removal.
2. **Dictionaries & Tolerant Retrieval** (Module 2): Handled in `src/indexer/index_builder.py` through Porter stemming and vocabulary indexing.
3. **Index Construction** (Module 3): `scripts/build_index.py` passes over the corpus, computes document frequencies (DF), and stores term positions.
4. **Scoring & Term Weighting** (Module 4): `src/retrieval/scorer.py` computes TF-IDF weights and handles Zone Scoring.
5. **Vector Space Model (VSM)** (Module 5): `src/retrieval/scorer.py` implements Cosine Similarity dot products between query vectors and document vectors.
6. **Evaluation** (Module 6): `src/evaluation/metrics.py` compares retrieved results against citation-based ground truth to produce MAP, Precision, and Recall.
