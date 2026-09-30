import json
import random
import os
from datetime import datetime, timedelta

# --- Realistic Patent Vocabulary by Domain ---
DOMAINS = {
    "G06F": {
        "name": "Computing / Digital Data Processing",
        "title_templates": [
            "Method and system for {adj} {noun} {verb} in {context}",
            "Apparatus for {adj} {noun} {verb} using {tech}",
            "System for {adj} {noun} management with {tech}",
            "{adj} {noun} {verb} method and apparatus",
            "Computer-implemented method for {adj} {noun} {verb}",
        ],
        "adjectives": ["distributed", "parallel", "adaptive", "real-time", "fault-tolerant",
                        "scalable", "dynamic", "optimized", "secure", "automated", "hybrid"],
        "nouns": ["data", "memory", "processor", "cache", "pipeline", "buffer", "register",
                  "scheduler", "compiler", "database", "file system", "instruction set", "thread",
                  "kernel", "operating system", "virtual machine", "container", "microservice"],
        "verbs": ["processing", "allocation", "optimization", "scheduling", "compression",
                  "decompression", "encryption", "sorting", "indexing", "caching", "partitioning"],
        "contexts": ["cloud computing environments", "multi-core architectures", "edge computing nodes",
                     "heterogeneous computing systems", "mobile computing devices",
                     "server clusters", "embedded systems", "distributed networks"],
        "techs": ["machine learning models", "neural network inference", "graph-based algorithms",
                  "heuristic search", "probabilistic data structures", "hash tables",
                  "binary search trees", "concurrent data structures"],
    },
    "H04W": {
        "name": "Wireless Communication Networks",
        "title_templates": [
            "Method for {adj} {noun} in {context}",
            "{adj} {noun} {verb} system for {context}",
            "Apparatus and method for {adj} {noun} {verb}",
            "System for {noun} {verb} using {tech}",
        ],
        "adjectives": ["adaptive", "cognitive", "cooperative", "energy-efficient",
                        "low-latency", "high-throughput", "multi-band", "full-duplex", "massive"],
        "nouns": ["antenna", "beamforming", "spectrum", "channel", "signal", "baseband",
                  "modulation", "handover", "relay", "interference", "bandwidth",
                  "carrier", "multiplexing", "OFDM subcarrier"],
        "verbs": ["allocation", "estimation", "detection", "cancellation", "tracking",
                  "scheduling", "mitigation", "equalization", "decoding"],
        "contexts": ["5G networks", "millimeter wave systems", "IoT sensor networks",
                     "vehicular ad-hoc networks", "satellite communication systems",
                     "heterogeneous wireless networks", "device-to-device communication"],
        "techs": ["MIMO antenna arrays", "cognitive radio techniques", "NOMA schemes",
                  "deep reinforcement learning", "compressed sensing", "reconfigurable intelligent surfaces"],
    },
    "G06N": {
        "name": "Computing Arrangements Based on Specific Models (AI/ML)",
        "title_templates": [
            "Method for {adj} {noun} using {tech}",
            "{adj} {noun} system for {context}",
            "Apparatus for {adj} {noun} {verb} with {tech}",
            "System and method for {noun} {verb} in {context}",
        ],
        "adjectives": ["deep", "generative", "adversarial", "self-supervised", "federated",
                        "attention-based", "transformer-based", "graph-based", "multi-modal",
                        "few-shot", "continual", "robust", "interpretable"],
        "nouns": ["neural network", "language model", "image classifier", "object detector",
                  "recommendation engine", "reinforcement learning agent", "knowledge graph",
                  "embedding", "feature extractor", "autoencoder", "diffusion model"],
        "verbs": ["training", "inference", "fine-tuning", "pruning", "quantization",
                  "distillation", "augmentation", "generation", "prediction", "classification"],
        "contexts": ["natural language processing", "computer vision tasks", "speech recognition",
                     "autonomous driving", "medical image analysis", "drug discovery",
                     "financial forecasting", "anomaly detection systems"],
        "techs": ["convolutional neural networks", "recurrent neural networks",
                  "transformer architectures", "variational autoencoders",
                  "generative adversarial networks", "graph neural networks",
                  "attention mechanisms", "contrastive learning"],
    },
    "H04L": {
        "name": "Transmission of Digital Information (Networking)",
        "title_templates": [
            "Method for {adj} {noun} in {context}",
            "{adj} {noun} {verb} apparatus",
            "System for {adj} {noun} {verb} in {context}",
            "Protocol for {adj} {noun} {verb} using {tech}",
        ],
        "adjectives": ["secure", "authenticated", "encrypted", "decentralized",
                        "load-balanced", "redundant", "resilient", "high-availability",
                        "software-defined", "programmable"],
        "nouns": ["packet", "routing", "firewall", "proxy", "gateway", "switch",
                  "protocol", "session", "certificate", "key", "token", "blockchain",
                  "smart contract", "consensus", "ledger", "transaction"],
        "verbs": ["forwarding", "filtering", "inspection", "authentication", "verification",
                  "encryption", "decryption", "signing", "validation", "mining"],
        "contexts": ["software-defined networks", "cloud-native architectures",
                     "peer-to-peer networks", "enterprise network infrastructure",
                     "Internet of Things deployments", "edge computing environments",
                     "blockchain networks", "zero-trust architectures"],
        "techs": ["public key infrastructure", "zero-knowledge proofs",
                  "homomorphic encryption", "trusted execution environments",
                  "distributed hash tables", "consensus algorithms"],
    },
    "A61B": {
        "name": "Medical Diagnosis / Surgery / Identification",
        "title_templates": [
            "Method for {adj} {noun} in {context}",
            "{adj} {noun} {verb} apparatus for {context}",
            "System for {adj} {noun} {verb} using {tech}",
            "Device for {noun} {verb} in {context}",
        ],
        "adjectives": ["minimally invasive", "robotic", "image-guided", "wearable",
                        "implantable", "non-invasive", "real-time", "portable",
                        "AI-assisted", "patient-specific"],
        "nouns": ["catheter", "endoscope", "ultrasound transducer", "biosensor",
                  "surgical instrument", "diagnostic probe", "imaging system",
                  "heart monitor", "blood pressure sensor", "neural interface",
                  "tissue analyzer", "biomarker detector"],
        "verbs": ["imaging", "monitoring", "stimulation", "ablation", "biopsy",
                  "detection", "measurement", "analysis", "tracking", "classification"],
        "contexts": ["cardiovascular procedures", "neurosurgical operations",
                     "orthopedic surgery", "ophthalmic diagnosis",
                     "cancer screening", "point-of-care testing",
                     "remote patient monitoring", "telemedicine"],
        "techs": ["magnetic resonance imaging", "computed tomography",
                  "optical coherence tomography", "photoacoustic imaging",
                  "deep learning classification", "MEMS sensors"],
    },
    "B60W": {
        "name": "Autonomous Vehicle Control",
        "title_templates": [
            "Method for {adj} {noun} in {context}",
            "{adj} {noun} {verb} system for {context}",
            "Apparatus for {adj} {noun} {verb} using {tech}",
            "Vehicle control system for {adj} {noun} {verb}",
        ],
        "adjectives": ["autonomous", "semi-autonomous", "adaptive", "predictive",
                        "cooperative", "multi-sensor", "trajectory-optimized",
                        "collision-avoidant", "V2X-enabled", "map-aware"],
        "nouns": ["path planner", "perception module", "localization system",
                  "LIDAR point cloud", "radar signal", "camera feed", "sensor fusion",
                  "motion planner", "behavior predictor", "control actuator",
                  "lane detector", "obstacle tracker"],
        "verbs": ["planning", "detection", "tracking", "fusion", "prediction",
                  "control", "navigation", "mapping", "calibration", "classification"],
        "contexts": ["highway driving scenarios", "urban intersections",
                     "parking environments", "adverse weather conditions",
                     "mixed traffic environments", "platooning formations"],
        "techs": ["deep neural networks", "Kalman filtering",
                  "particle filter localization", "model predictive control",
                  "simultaneous localization and mapping", "reinforcement learning policies"],
    },
    "G06T": {
        "name": "Image Data Processing / Computer Graphics",
        "title_templates": [
            "Method for {adj} {noun} {verb}",
            "{adj} {noun} {verb} system for {context}",
            "Apparatus for {adj} {noun} {verb} using {tech}",
            "System for {noun} {verb} in {context}",
        ],
        "adjectives": ["high-resolution", "real-time", "3D", "volumetric",
                        "multi-scale", "neural", "differentiable", "photorealistic",
                        "panoramic", "stereoscopic"],
        "nouns": ["image", "texture", "mesh", "point cloud", "voxel grid",
                  "scene", "rendering pipeline", "ray tracer", "shader",
                  "segmentation map", "depth map", "surface normal"],
        "verbs": ["rendering", "reconstruction", "segmentation", "super-resolution",
                  "inpainting", "denoising", "registration", "compositing",
                  "synthesis", "compression", "enhancement"],
        "contexts": ["augmented reality applications", "virtual reality environments",
                     "medical image analysis", "satellite imagery processing",
                     "autonomous navigation", "video game engines",
                     "film post-production", "digital twin simulations"],
        "techs": ["convolutional neural networks", "neural radiance fields",
                  "generative adversarial networks", "variational autoencoders",
                  "graph convolutional networks", "signed distance functions"],
    },
}

ASSIGNEES = [
    "Google LLC", "Apple Inc.", "Microsoft Technology Licensing LLC",
    "Samsung Electronics Co. Ltd.", "IBM Corporation", "Amazon Technologies Inc.",
    "Meta Platforms Inc.", "Intel Corporation", "Qualcomm Incorporated",
    "NVIDIA Corporation", "Huawei Technologies Co. Ltd.", "Sony Group Corporation",
    "Toyota Motor Corporation", "Siemens Healthineers AG", "Medtronic Inc.",
    "Cisco Systems Inc.", "Oracle International Corporation",
    "Tencent Holdings Limited", "Baidu Inc.", "ByteDance Ltd.",
]


def fill_template(template, domain_data):
    return template.format(
        adj=random.choice(domain_data["adjectives"]),
        noun=random.choice(domain_data["nouns"]),
        verb=random.choice(domain_data["verbs"]),
        context=random.choice(domain_data["contexts"]),
        tech=random.choice(domain_data["techs"]),
    )


def generate_paragraph(domain_data, min_sentences=3, max_sentences=8):
    """Generate a realistic paragraph mixing domain vocabulary."""
    sentences = []
    for _ in range(random.randint(min_sentences, max_sentences)):
        pattern = random.choice([
            "The {adj} {noun} performs {verb} within {context} using {tech}.",
            "A {adj} {noun} is configured for {verb} in {context}.",
            "The system includes a {adj} {noun} module that enables {verb}.",
            "In one embodiment, the {adj} {noun} achieves improved {verb} by utilizing {tech}.",
            "The disclosed {noun} provides efficient {verb} for {context}.",
            "According to the present invention, a {adj} {noun} is provided for {verb} in {context}.",
            "The {noun} is coupled with {tech} to facilitate {verb}.",
            "Further, the {adj} {noun} may be adapted for {verb} based on {tech}.",
        ])
        sentences.append(fill_template(pattern, domain_data))
    return " ".join(sentences)


def generate_claims(domain_data, num_claims=5):
    """Generate patent claim text."""
    claims = []
    for i in range(1, num_claims + 1):
        if i == 1:
            claim = f"{i}. A method for {fill_template('{adj} {noun} {verb} in {context}', domain_data)}, comprising: "
        elif random.random() < 0.4:
            dep = random.randint(1, i - 1)
            claim = f"{i}. The method of claim {dep}, further comprising: "
        else:
            claim = f"{i}. A system for {fill_template('{adj} {noun} {verb} using {tech}', domain_data)}, comprising: "

        steps = []
        for _ in range(random.randint(2, 4)):
            step = fill_template(
                random.choice([
                    "receiving, by a {noun}, data associated with {adj} {verb}",
                    "processing the received data using {tech} to perform {verb}",
                    "generating a {adj} {noun} based on the {verb} result",
                    "transmitting the {adj} output to a {noun} in {context}",
                ]),
                domain_data,
            )
            steps.append(step)
        claim += "; ".join(steps) + "."
        claims.append(claim)
    return " ".join(claims)


def generate_dummy_patents(num_patents, output_file):
    random.seed(42)  # Reproducibility
    patents = []
    cpc_keys = list(DOMAINS.keys())

    for i in range(num_patents):
        patent_id = f"US{10000000 + i}B2"
        cpc = random.choice(cpc_keys)
        domain = DOMAINS[cpc]

        days_ago = random.randint(0, 365 * 10)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        title = fill_template(random.choice(domain["title_templates"]), domain)
        abstract = generate_paragraph(domain, 2, 4)
        claims_text = generate_claims(domain, random.randint(3, 7))
        description = generate_paragraph(domain, 6, 12)
        assignee = random.choice(ASSIGNEES)

        patent = {
            "id": patent_id,
            "date": date,
            "cpc": cpc,
            "assignee": assignee,
            "title": title,
            "abstract": abstract,
            "claims": claims_text,
            "description": description,
        }
        patents.append(patent)

    # --- Generate citation links (for evaluation ground truth) ---
    # Each patent cites 0-5 earlier patents. Same CPC = higher probability.
    for i, patent in enumerate(patents):
        num_citations = random.randint(0, min(5, i))
        candidates = list(range(max(0, i - 50), i))  # cite from recent 50
        if not candidates:
            patent["citations"] = []
            continue
        # Bias toward same CPC class
        same_cpc = [j for j in candidates if patents[j]["cpc"] == patent["cpc"]]
        diff_cpc = [j for j in candidates if patents[j]["cpc"] != patent["cpc"]]
        pool = same_cpc * 3 + diff_cpc  # 3x weight for same CPC
        if not pool:
            pool = candidates
        cited_indices = random.sample(pool, min(num_citations, len(pool)))
        patent["citations"] = [patents[j]["id"] for j in set(cited_indices)]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(patents, f, indent=2)

    print(f"Generated {num_patents} realistic patents -> {output_file}")

    # --- Generate labeled evaluation queries ---
    queries = []
    sampled = random.sample(range(len(patents)), min(30, len(patents)))
    for idx in sampled:
        p = patents[idx]
        # Query = partial abstract rewrite + claim snippet
        query_text = " ".join(p["abstract"].split()[:20]) + " " + " ".join(p["claims"].split()[:15])
        relevant = [p["id"]] + p.get("citations", [])
        queries.append({
            "query_id": f"Q{idx:04d}",
            "query_text": query_text,
            "relevant_patents": relevant,
            "source_patent": p["id"],
        })

    queries_path = os.path.join(os.path.dirname(output_file), "..", "queries", "evaluation_queries.json")
    os.makedirs(os.path.dirname(queries_path), exist_ok=True)
    with open(queries_path, "w", encoding="utf-8") as f:
        json.dump(queries, f, indent=2)
    print(f"Generated {len(queries)} evaluation queries -> {queries_path}")


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "patents.json")
    generate_dummy_patents(500, output_path)
