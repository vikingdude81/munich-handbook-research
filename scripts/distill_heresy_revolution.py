#!/usr/bin/env python
"""
Distill & analyze Heresy & Revolution PDFs using deconstructionist/constructive framework.
Extracts entropy scores, scapegoats, rhetorical intensity, and constructive proposals.

Usage:
    python scripts/distill_heresy_revolution.py --source malleus_maleficarum
    python scripts/distill_heresy_revolution.py --source karl_marx
    python scripts/distill_heresy_revolution.py --analyze-cross-doc
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)-5s %(message)s')
logger = logging.getLogger(__name__)


EXTRACTION_PROMPT_TEMPLATE = """You are an analytical engine analyzing historical texts for deconstructionist and constructive rhetoric patterns.

Your task: Evaluate the provided text chunk and classify its operational utility, extracting specific indicators of either critique/destruction or building/governance.

Definitions:
- Deconstructionist Rhetoric: Text focused on criticizing, dismantling, or exposing flaws of the current system, hierarchy, or enemy. Points out failure points but does not explain how to govern.
- Constructive Mechanisms: Text focused on building, governing, or maintaining a functional replacement system. Contains specific rules, administrative structures, or protocols.

Analyze the chunk and respond with ONLY a valid JSON object (no markdown, no extra text):

{
  "primary_mode": "Deconstruction" | "Construction" | "Mixed" | "Neutral",
  "deconstruction_targets": ["entities or concepts to destroy/criticize"],
  "constructive_proposals": ["specific rules, mechanisms, structures for replacement"],
  "rhetorical_intensity": 1-10,
  "entropy_score": 1-10,
  "semantic_markers_matched": {
    "deconstructionist": ["matched words from: abolish, dismantle, expose, exploit, parasitic, chains, corrupt, eradicate, overthrow, subvert, illusion, uproot, usurp, tyranny, oppression"],
    "constructive": ["matched words from: establish, maintain, govern, structure, balance, generate, cultivate, administer, protocol, law, order, sustain, mechanism, framework, principle"]
  },
  "scapegoat_identified": {
    "name": "The primary enemy or target of condemnation",
    "attributes": ["listed evils attributed to the scapegoat"],
    "justification": "How/why the text justifies focus on this entity"
  },
  "moral_justification": "Summary of how extreme measures are rationalized",
  "summary": "2-3 sentence analysis of this chunk's contribution to the overall argument"
}

TEXT TO ANALYZE:
---
{chunk_text}
---

Respond with only the JSON object."""


class HerasyRevolutionDistiller:
    """Distill Heresy & Revolution PDFs through entropy & deconstruction analysis."""
    
    DECONSTRUCTIONIST_MARKERS = {
        'abolish', 'dismantle', 'expose', 'exploit', 'parasitic', 'chains',
        'corrupt', 'eradicate', 'overthrow', 'subvert', 'illusion', 'uproot',
        'usurp', 'tyranny', 'oppression', 'enslavement', 'corruption', 'decay',
        'rot', 'poison', 'disease', 'infection', 'plague', 'curse', 'destroy',
        'annihilate', 'obliterate', 'eliminate', 'wipe out', 'purge'
    }
    
    CONSTRUCTIVE_MARKERS = {
        'establish', 'maintain', 'govern', 'structure', 'balance', 'generate',
        'cultivate', 'administer', 'protocol', 'law', 'order', 'sustain',
        'mechanism', 'framework', 'principle', 'regulation', 'system', 'design',
        'construct', 'build', 'create', 'organize', 'coordinate', 'function',
        'operate', 'rule', 'direct', 'manage', 'control', 'implement'
    }
    
    def __init__(self, model_name: str = 'qwen3.5:9b'):
        """Initialize with LM Studio connection."""
        self.model_name = model_name
        # Will attempt to connect to local LM Studio instance
        self.base_url = 'http://localhost:8000'
        self.client = None
        
        try:
            from openai import OpenAI
            self.client = OpenAI(base_url=self.base_url, api_key='lm-studio')
            logger.info(f"Initialized LM Studio client ({model_name})")
        except Exception as e:
            logger.warning(f"LM Studio connection failed: {e}")
    
    def extract_chunk_analysis(self, chunk_text: str, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Extract analysis for a single chunk using LLM."""
        if not self.client:
            logger.warning(f"  [{chunk_id}] Skipping: LM Studio not available")
            return None
        
        try:
            prompt = EXTRACTION_PROMPT_TEMPLATE.format(chunk_text=chunk_text[:2000])
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown wrapping)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning(f"  [{chunk_id}] No JSON found in response")
                return None
            
            analysis = json.loads(json_match.group())
            logger.info(f"  [{chunk_id}] entropy={analysis.get('entropy_score', '?')}, "
                       f"intensity={analysis.get('rhetorical_intensity', '?')}, "
                       f"mode={analysis.get('primary_mode', '?')}")
            
            return analysis
        
        except json.JSONDecodeError as e:
            logger.warning(f"  [{chunk_id}] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"  [{chunk_id}] Extraction error: {e}")
            return None
    
    def distill_source(self, source_id: str, chunks_dir: Path) -> bool:
        """Distill all chunks from a source."""
        if not chunks_dir.exists():
            logger.error(f"Chunks directory not found: {chunks_dir}")
            return False
        
        chunk_files = sorted(chunks_dir.glob('chunk_*.txt'))
        if not chunk_files:
            logger.error(f"No chunks found in {chunks_dir}")
            return False
        
        logger.info(f"Distilling [{source_id}] ({len(chunk_files)} chunks)")
        
        analyses = []
        failed = []
        
        for chunk_file in chunk_files:
            chunk_id = chunk_file.stem
            chunk_text = chunk_file.read_text(encoding='utf-8')
            
            analysis = self.extract_chunk_analysis(chunk_text, chunk_id)
            
            if analysis:
                analysis['chunk_id'] = chunk_id
                analysis['source_size'] = len(chunk_text)
                analyses.append(analysis)
            else:
                failed.append(chunk_id)
        
        if not analyses:
            logger.error(f"No successful analyses for {source_id}")
            return False
        
        # Save analyses
        output_dir = Path(f'data/distilled/malleus_marx')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Individual analysis files
        for analysis in analyses:
            analysis_file = output_dir / f'{source_id}_{analysis["chunk_id"]}.json'
            analysis_file.write_text(json.dumps(analysis, indent=2), encoding='utf-8')
        
        # Aggregate
        aggregate = {
            'source': source_id,
            'total_chunks': len(chunk_files),
            'successful': len(analyses),
            'failed': len(failed),
            'summary_stats': self._compute_summary_stats(analyses),
            'analyses': analyses
        }
        
        aggregate_file = output_dir / f'{source_id}_aggregate.json'
        aggregate_file.write_text(json.dumps(aggregate, indent=2), encoding='utf-8')
        
        logger.info(f"  Saved {len(analyses)} analyses to {output_dir}")
        if failed:
            logger.warning(f"  Failed chunks: {', '.join(failed)}")
        
        return True
    
    def _compute_summary_stats(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Compute aggregate statistics across chunks."""
        entropy_scores = [a.get('entropy_score', 0) for a in analyses if a.get('entropy_score')]
        intensity_scores = [a.get('rhetorical_intensity', 0) for a in analyses if a.get('rhetorical_intensity')]
        
        if not entropy_scores:
            return {}
        
        return {
            'avg_entropy': sum(entropy_scores) / len(entropy_scores),
            'max_entropy': max(entropy_scores),
            'min_entropy': min(entropy_scores),
            'avg_intensity': sum(intensity_scores) / len(intensity_scores) if intensity_scores else 0,
            'mode_distribution': self._get_mode_distribution(analyses),
            'high_void_count': sum(1 for a in analyses 
                                   if a.get('entropy_score', 0) >= 8 
                                   and len(a.get('constructive_proposals', [])) == 0),
        }
    
    def _get_mode_distribution(self, analyses: List[Dict]) -> Dict[str, int]:
        """Count distribution of primary_mode values."""
        from collections import Counter
        modes = [a.get('primary_mode', 'Unknown') for a in analyses]
        return dict(Counter(modes))
    
    def cross_document_analysis(self, output_dir: Path = Path('data/distilled/malleus_marx')) -> bool:
        """Analyze patterns across both documents."""
        malleus_file = output_dir / 'malleus_maleficarum_aggregate.json'
        marx_file = output_dir / 'karl_marx_aggregate.json'
        
        if not malleus_file.exists() or not marx_file.exists():
            logger.error("Both source aggregates must exist for cross-document analysis")
            return False
        
        malleus_data = json.loads(malleus_file.read_text(encoding='utf-8'))
        marx_data = json.loads(marx_file.read_text(encoding='utf-8'))
        
        logger.info("Performing cross-document analysis …")
        
        cross_analysis = {
            'sources': ['malleus_maleficarum', 'karl_marx'],
            'malleus_stats': malleus_data.get('summary_stats', {}),
            'marx_stats': marx_data.get('summary_stats', {}),
            'scapegoat_mapping': self._map_scapegoats(
                malleus_data.get('analyses', []),
                marx_data.get('analyses', [])
            ),
            'entropy_comparison': {
                'malleus_avg': malleus_data.get('summary_stats', {}).get('avg_entropy', 0),
                'marx_avg': marx_data.get('summary_stats', {}).get('avg_entropy', 0),
            },
            'void_analysis': {
                'malleus_high_void': malleus_data.get('summary_stats', {}).get('high_void_count', 0),
                'marx_high_void': marx_data.get('summary_stats', {}).get('high_void_count', 0),
                'interpretation': 'High void count = many chunks with high rhetorical intensity but zero constructive proposals'
            }
        }
        
        analysis_file = output_dir / 'cross_document_analysis.json'
        analysis_file.write_text(json.dumps(cross_analysis, indent=2), encoding='utf-8')
        
        logger.info(f"  Cross-document analysis saved to {analysis_file}")
        logger.info(f"  Malleus avg entropy: {cross_analysis['entropy_comparison']['malleus_avg']:.2f}")
        logger.info(f"  Marx avg entropy: {cross_analysis['entropy_comparison']['marx_avg']:.2f}")
        logger.info(f"  Malleus high-void chunks: {cross_analysis['void_analysis']['malleus_high_void']}")
        logger.info(f"  Marx high-void chunks: {cross_analysis['void_analysis']['marx_high_void']}")
        
        return True
    
    def _map_scapegoats(self, malleus_analyses: List[Dict], marx_analyses: List[Dict]) -> Dict[str, Any]:
        """Map scapegoat entities between documents."""
        malleus_scapegoats = [
            a.get('scapegoat_identified', {}).get('name', '')
            for a in malleus_analyses
            if a.get('scapegoat_identified', {}).get('name')
        ]
        
        marx_scapegoats = [
            a.get('scapegoat_identified', {}).get('name', '')
            for a in marx_analyses
            if a.get('scapegoat_identified', {}).get('name')
        ]
        
        return {
            'malleus_scapegoats': list(set(malleus_scapegoats)),
            'marx_scapegoats': list(set(marx_scapegoats)),
            'note': 'See semantic analysis for mapping patterns'
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Distill Heresy & Revolution PDFs through entropy & deconstructionist analysis'
    )
    parser.add_argument(
        '--source',
        choices=['malleus_maleficarum', 'karl_marx'],
        help='Which source to distill'
    )
    parser.add_argument(
        '--analyze-cross-doc',
        action='store_true',
        help='Run cross-document analysis after both sources are distilled'
    )
    parser.add_argument(
        '--model',
        default='qwen3.5:9b',
        help='LM Studio model name'
    )
    
    args = parser.parse_args()
    
    distiller = HerasyRevolutionDistiller(model_name=args.model)
    
    if args.source == 'malleus_maleficarum':
        chunks_dir = Path('data/sources/malleus_marx/malleus_maleficarum')
        success = distiller.distill_source('malleus_maleficarum', chunks_dir)
    elif args.source == 'karl_marx':
        chunks_dir = Path('data/sources/malleus_marx/karl_marx')
        success = distiller.distill_source('karl_marx', chunks_dir)
    elif args.analyze_cross_doc:
        success = distiller.cross_document_analysis()
    else:
        logger.error("Must specify --source or --analyze-cross-doc")
        sys.exit(1)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
