"""
Source Preparation Script for Munich Handbook Research
Generates source_manifest.json with chunked, embedded text data.
"""

import json
import hashlib
from pathlib import Path

# Source files to process
SOURCE_FILES = [
    {
        "path": "Agrippa_De_Occulta_Philosophia.txt",
        "categories": ["demonology", "occult", "medieval", "hermetic"],
        "max_tokens": 512,
        "overlap": 64
    },
    {
        "path": "Picatrix_Liber_Apoteles.txt",
        "categories": ["demonology", "occult", "arabic", "hermetic"],
        "max_tokens": 512,
        "overlap": 64
    },
    {
        "path": "Bavarian_Stadtbuch_Witchcraft_Statutes.txt",
        "categories": ["legal", "statute", "medieval", "bavaria"],
        "max_tokens": 512,
        "overlap": 64
    },
    {
        "path": "FTTF_Fournier_Trial_Records.txt",
        "categories": ["legal", "trial", "medieval", "witchcraft"],
        "max_tokens": 512,
        "overlap": 64
    }
]

# Simulated embeddings (in production, would use actual embedding model)
def generate_embedding(text):
    """Generate a simulated embedding vector."""
    # In production: use sentence-transformers or Ollama nomic-embed-text
    # For now, return a deterministic hash-based vector
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    dim = 768  # Standard embedding dimension
    return [float((hash_val + i) % 1000 - 500) / 500 for i in range(dim)]

def chunk_text(text, max_tokens=512, overlap=64):
    """Chunk text with sliding window."""
    # Simple token approximation (1 token ≈ 4 characters)
    max_chars = max_tokens * 4
    chunks = []
    
    for i in range(0, len(text), max_chars - overlap):
        chunk = text[i:i + max_chars]
        if len(chunk) > overlap:
            chunks.append(chunk)
    
    return chunks

def process_source(filepath, categories):
    """Process a single source file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text(text)
    manifest_chunks = []
    
    for idx, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)
        chunk_id = f"{filepath.stem}-chunk-{idx:03d}"
        
        # Extract metadata from chunk
        page = 1
        section = "General"
        entity_mentions = []
        
        # Simple entity detection
        if "Mercury" in chunk:
            entity_mentions.append("Mercury")
        if "demon" in chunk.lower():
            entity_mentions.append("demon")
        if "Vapula" in chunk:
            entity_mentions.append("Vapula")
        if "Forculus" in chunk:
            entity_mentions.append("Forculus")
        
        manifest_chunk = {
            "id": chunk_id,
            "source_file": str(filepath),
            "text": chunk.strip(),
            "embedding": embedding,
            "metadata": {
                "page": page,
                "section": section,
                "entity_mentions": entity_mentions,
                "categories": categories
            }
        }
        manifest_chunks.append(manifest_chunk)
    
    return manifest_chunks

def main():
    base_dir = Path("E:/munich-handbook-research/data/sources")
    output_path = base_dir / "source_manifest.json"
    
    all_chunks = []
    total_chars = 0
    
    for source in SOURCE_FILES:
        filepath = base_dir / source["path"]
        if not filepath.exists():
            print(f"Warning: {filepath} not found, skipping...")
            continue
        
        print(f"Processing {source['path']}...")
        chunks = process_source(filepath, source["categories"])
        all_chunks.extend(chunks)
        total_chars += len(chunks[0]) if chunks else 0
    
    # Create manifest
    manifest = {
        "version": "v2",
        "chunks": all_chunks,
        "metadata": {
            "total_chunks": len(all_chunks),
            "avg_embedding_dim": 768,
            "sources_processed": len([s for s in SOURCE_FILES if (base_dir / s["path"]).exists()])
        }
    }
    
    # Write manifest
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nManifest written to: {output_path}")
    print(f"Total chunks generated: {len(all_chunks)}")
    print(f"Average embedding dimension: 768")
    print(f"Sources processed: {manifest['metadata']['sources_processed']}")

if __name__ == "__main__":
    main()
