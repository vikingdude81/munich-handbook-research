#!/usr/bin/env python
"""
Ingest PDFs for Heresy & Revolution analysis.
Extracts text from Malleus Maleficarum and Karl Marx works, chunks them.

Usage:
    python scripts/ingest_heresy_revolution.py --pdf malleus --chunk-size 10000
    python scripts/ingest_heresy_revolution.py --pdf marx --chunk-size 10000
    python scripts/ingest_heresy_revolution.py --pdf all
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Try to import PyPDF2 for PDF extraction
try:
    import PyPDF2
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    print("WARNING: PyPDF2 not installed. Install with: pip install PyPDF2")

logging.basicConfig(level=logging.INFO, format='%(levelname)-5s %(message)s')
logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """Extract text from PDF files with chunking support."""
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract all text from a PDF file."""
        if not HAS_PYPDF:
            raise ImportError("PyPDF2 required. Install with: pip install PyPDF2")
        
        text = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            logger.info(f"  {len(reader.pages)} pages detected")
            
            for page_num, page in enumerate(reader.pages, 1):
                if page_num % 50 == 0:
                    logger.info(f"  Reading page {page_num}/{len(reader.pages)} …")
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                except Exception as e:
                    logger.warning(f"  Page {page_num}: extraction error: {e}")
        
        full_text = '\n'.join(text)
        return full_text
    
    def chunk_text(self, text: str) -> List[Dict[str, str]]:
        """Split text into chunks, preserving context."""
        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'size': current_size
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Save final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'size': current_size
            })
        
        return chunks


def ingest_malleus(chunk_size: int = 10000):
    """Ingest The Malleus Maleficarum PDF."""
    pdf_path = Path('c:/Users/akbon/Downloads/The Malleus Maleficarum.pdf')
    output_dir = Path('data/sources/malleus_marx/malleus_maleficarum')
    
    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return False
    
    logger.info(f"Extracting [Malleus Maleficarum] …")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        extractor = PDFTextExtractor(chunk_size=chunk_size)
        logger.info("  Extracting text from PDF …")
        full_text = extractor.extract_text(pdf_path)
        logger.info(f"  Extracted {len(full_text):,} chars")
        
        logger.info("  Chunking …")
        chunks = extractor.chunk_text(full_text)
        logger.info(f"  {len(chunks)} chunks of ~{chunk_size} chars")
        
        # Write chunks
        for i, chunk in enumerate(chunks):
            chunk_path = output_dir / f'chunk_{i:03d}.txt'
            chunk_path.write_text(chunk['text'], encoding='utf-8')
        
        logger.info(f"  Written to {output_dir}")
        return True
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return False


def ingest_marx(chunk_size: int = 10000):
    """Ingest Selected Works of Karl Marx PDF."""
    pdf_path = Path('c:/Users/akbon/Downloads/selected-works-karl-marx.pdf')
    output_dir = Path('data/sources/malleus_marx/karl_marx')
    
    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return False
    
    logger.info(f"Extracting [Selected Works of Karl Marx] …")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        extractor = PDFTextExtractor(chunk_size=chunk_size)
        logger.info("  Extracting text from PDF …")
        full_text = extractor.extract_text(pdf_path)
        logger.info(f"  Extracted {len(full_text):,} chars")
        
        logger.info("  Chunking …")
        chunks = extractor.chunk_text(full_text)
        logger.info(f"  {len(chunks)} chunks of ~{chunk_size} chars")
        
        # Write chunks
        for i, chunk in enumerate(chunks):
            chunk_path = output_dir / f'chunk_{i:03d}.txt'
            chunk_path.write_text(chunk['text'], encoding='utf-8')
        
        logger.info(f"  Written to {output_dir}")
        return True
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return False


def update_source_manifest():
    """Update source_manifest.json with new project entries."""
    manifest_path = Path('data/sources/source_manifest.json')
    
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    else:
        manifest = {'sources': []}
    
    # Add malleus_maleficarum if not present
    if not any(s['id'] == 'malleus_maleficarum' for s in manifest.get('sources', [])):
        manifest['sources'].append({
            'id': 'malleus_maleficarum',
            'title': 'The Malleus Maleficarum (1486)',
            'authors': ['Heinrich Kramer', 'Jacob Sprenger'],
            'year': 1486,
            'project': 'malleus_marx',
            'status': 'ingested',
            'chunks': 'data/sources/malleus_marx/malleus_maleficarum',
            'description': 'Medieval heresy prosecution manual — deconstructionist rhetoric analysis'
        })
    
    # Add karl_marx if not present
    if not any(s['id'] == 'karl_marx' for s in manifest.get('sources', [])):
        manifest['sources'].append({
            'id': 'karl_marx',
            'title': 'Selected Works of Karl Marx',
            'authors': ['Karl Marx'],
            'year': 1848,
            'project': 'malleus_marx',
            'status': 'ingested',
            'chunks': 'data/sources/malleus_marx/karl_marx',
            'description': 'Revolutionary socialist critique — deconstructionist rhetoric analysis'
        })
    
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    logger.info(f"Manifest updated: {manifest_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ingest PDFs for Heresy & Revolution analysis')
    parser.add_argument(
        '--pdf',
        choices=['malleus', 'marx', 'all'],
        default='all',
        help='Which PDF(s) to ingest'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=10000,
        help='Target chunk size in characters'
    )
    
    args = parser.parse_args()
    
    success = True
    
    if args.pdf in ['malleus', 'all']:
        if not ingest_malleus(chunk_size=args.chunk_size):
            success = False
    
    if args.pdf in ['marx', 'all']:
        if not ingest_marx(chunk_size=args.chunk_size):
            success = False
    
    if success:
        update_source_manifest()
        logger.info("Done. Ready for extraction pipeline.")
    else:
        logger.error("Ingestion incomplete. Check errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
