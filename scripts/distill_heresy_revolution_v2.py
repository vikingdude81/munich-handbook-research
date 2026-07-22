#!/usr/bin/env python3
"""
Distill Heresy & Revolution PDFs using the proven pipeline.py approach.
Extracts entropy scores, scapegoats, rhetorical intensity, constructive proposals.

Usage:
    python scripts/distill_heresy_revolution_v2.py --source malleus_maleficarum
    python scripts/distill_heresy_revolution_v2.py --source karl_marx
    python scripts/distill_heresy_revolution_v2.py --analyze-cross
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from openai import OpenAI

# ── Config ─────────────────────────────────────────────────────────────────
LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL = "nvidia/nemotron-3-nano-omni"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# ── Prompts ────────────────────────────────────────────────────────────────

DISTILL_SYSTEM = (
    "You are a precise historical analyst specializing in rhetoric analysis. "
    "Extract deconstructionist vs. constructive rhetoric patterns from historical texts. "
    "Output only valid, complete JSON. Never invent data not in the source."
)

DISTILL_USER_TEMPLATE = """\
Analyze this passage for deconstructionist vs. constructive rhetoric patterns.

Research goal: Identify entropy (destruction vs. building), rhetorical intensity (moral condemnation), scapegoating, and constructive proposals.

Source text:
{text}

Return ONLY a JSON object with this exact schema:
{{
  "has_relevant_content": true/false,
  "primary_mode": "Deconstruction" or "Construction" or "Mixed" or "Neutral",
  "entropy_score": 1-10,
  "rhetorical_intensity": 1-10,
  "deconstruction_targets": ["entity1", "entity2"],
  "constructive_proposals": ["proposal1", "proposal2"],
  "scapegoat": {{
    "name": "identified enemy",
    "attributes": ["attribute1", "attribute2"],
    "justification": "why this is the target"
  }},
  "moral_justification": "how extreme measures are justified",
  "summary": "1-2 sentence summary"
}}

Definitions:
- Entropy Score: 1=purely constructive/ordered, 10=purely destructive/deconstructionist
- Rhetorical Intensity: 1=calm observation, 10=absolute moral condemnation
- High Void: entropy >= 8 AND constructive_proposals is empty = intense rhetoric without solutions
"""

def main():
    parser = argparse.ArgumentParser(description="Distill Heresy & Revolution PDFs")
    parser.add_argument('--source', choices=['malleus_maleficarum', 'karl_marx'], help='Source to distill')
    parser.add_argument('--analyze-cross', action='store_true', help='Cross-document analysis')
    parser.add_argument('--resume', action='store_true', help='Skip completed chunks')
    args = parser.parse_args()
    
    client = OpenAI(base_url=LM_STUDIO_URL, api_key='lm-studio')
    
    if args.source == 'malleus_maleficarum':
        distill_source('malleus_maleficarum', client, args.resume)
    elif args.source == 'karl_marx':
        distill_source('karl_marx', client, args.resume)
    elif args.analyze_cross:
        cross_document_analysis()
    else:
        parser.print_help()


def distill_source(source_id: str, client: OpenAI, resume: bool = False):
    """Distill all chunks for a source."""
    chunks_dir = DATA_DIR / 'sources' / 'malleus_marx' / source_id
    out_dir = DATA_DIR / 'distilled' / 'malleus_marx'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not chunks_dir.exists():
        print(f"ERROR: Chunks not found in {chunks_dir}")
        return False
    
    chunk_files = sorted(chunks_dir.glob('chunk_*.txt'))
    if not chunk_files:
        print(f"ERROR: No chunks found in {chunks_dir}")
        return False
    
    print(f"\nDistilling [{source_id}] ({len(chunk_files)} chunks)")
    
    successful = 0
    failed = 0
    
    for chunk_file in chunk_files:
        chunk_num = int(re.search(r'chunk_(\d+)', chunk_file.name).group(1))
        out_path = out_dir / f'{source_id}_chunk_{chunk_num:03d}.json'
        
        if resume and out_path.exists():
            continue
        
        chunk_text = chunk_file.read_text(encoding='utf-8')
        if len(chunk_text) > 8000:
            chunk_text = chunk_text[:8000]
        
        user_msg = DISTILL_USER_TEMPLATE.format(text=chunk_text)
        
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {'role': 'system', 'content': DISTILL_SYSTEM},
                        {'role': 'user', 'content': user_msg},
                        {'role': 'assistant', 'content': '{\n  "has_relevant_content":'},
                    ],
                    max_tokens=1200,
                    temperature=0.1,
                )
                
                raw = '{\n  "has_relevant_content":' + (resp.choices[0].message.content or '')
                
                # Parse with recovery
                raw = re.sub(r',\s*([}\]])', r'\1', raw)
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    # Try to salvage what we can
                    data = {
                        'has_relevant_content': 'has_relevant_content": true' in raw or 'has_relevant_content": false' not in raw,
                        'primary_mode': 'Unknown',
                        'entropy_score': 0,
                        'rhetorical_intensity': 0,
                        'summary': 'Parse error',
                        'error': 'Partial parse'
                    }
                
                data['source_id'] = source_id
                data['chunk_id'] = chunk_num
                out_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
                
                entropy = data.get('entropy_score', '?')
                intensity = data.get('rhetorical_intensity', '?')
                mode = data.get('primary_mode', '?')
                print(f"  chunk_{chunk_num:03d}: entropy={entropy}, intensity={intensity}, mode={mode}")
                successful += 1
                break
                
            except Exception as e:
                if attempt == 2:
                    print(f"  chunk_{chunk_num:03d}: ERROR - {e}")
                    out_path.write_text(json.dumps({
                        'source_id': source_id,
                        'chunk_id': chunk_num,
                        'error': str(e),
                        'has_relevant_content': False
                    }, indent=2))
                    failed += 1
                time.sleep(2 ** attempt)
    
    # Generate aggregate
    json_files = sorted(out_dir.glob(f'{source_id}_chunk_*.json'))
    if json_files:
        analyses = [json.loads(f.read_text(encoding='utf-8')) for f in json_files]
        
        entropy_scores = [a.get('entropy_score', 0) for a in analyses if isinstance(a.get('entropy_score'), (int, float))]
        intensity_scores = [a.get('rhetorical_intensity', 0) for a in analyses if isinstance(a.get('rhetorical_intensity'), (int, float))]
        
        aggregate = {
            'source': source_id,
            'total_chunks': len(chunk_files),
            'successful': successful,
            'failed': failed,
            'stats': {
                'avg_entropy': sum(entropy_scores) / len(entropy_scores) if entropy_scores else 0,
                'max_entropy': max(entropy_scores) if entropy_scores else 0,
                'min_entropy': min(entropy_scores) if entropy_scores else 0,
                'avg_intensity': sum(intensity_scores) / len(intensity_scores) if intensity_scores else 0,
                'high_void_count': sum(1 for a in analyses 
                                      if a.get('entropy_score', 0) >= 8 
                                      and len(a.get('constructive_proposals', [])) == 0),
            }
        }
        
        agg_path = out_dir / f'{source_id}_aggregate.json'
        agg_path.write_text(json.dumps(aggregate, indent=2), encoding='utf-8')
        print(f"\n  Aggregate saved to {agg_path}")
        print(f"  Avg entropy: {aggregate['stats']['avg_entropy']:.2f}")
        print(f"  High-void chunks: {aggregate['stats']['high_void_count']}")
    
    return True


def cross_document_analysis():
    """Compare malleus vs. marx."""
    out_dir = DATA_DIR / 'distilled' / 'malleus_marx'
    
    malleus_agg = out_dir / 'malleus_maleficarum_aggregate.json'
    marx_agg = out_dir / 'karl_marx_aggregate.json'
    
    if not (malleus_agg.exists() and marx_agg.exists()):
        print("ERROR: Both source aggregates must exist")
        return False
    
    malleus_data = json.loads(malleus_agg.read_text(encoding='utf-8'))
    marx_data = json.loads(marx_agg.read_text(encoding='utf-8'))
    
    print("\n" + "="*80)
    print("CROSS-DOCUMENT ANALYSIS: Malleus Maleficarum vs. Karl Marx")
    print("="*80)
    
    print(f"\nMALLEUS MALEFICARUM (1486):")
    print(f"  Avg Entropy: {malleus_data['stats']['avg_entropy']:.2f} (1=constructive, 10=destructive)")
    print(f"  Avg Rhetorical Intensity: {malleus_data['stats']['avg_intensity']:.2f}")
    print(f"  High-Void Chunks: {malleus_data['stats']['high_void_count']} (intense but no solutions)")
    
    print(f"\nKARL MARX (1848):")
    print(f"  Avg Entropy: {marx_data['stats']['avg_entropy']:.2f}")
    print(f"  Avg Rhetorical Intensity: {marx_data['stats']['avg_intensity']:.2f}")
    print(f"  High-Void Chunks: {marx_data['stats']['high_void_count']}")
    
    entropy_diff = marx_data['stats']['avg_entropy'] - malleus_data['stats']['avg_entropy']
    print(f"\nENTROPY DELTA: {entropy_diff:+.2f} (Marx more {'destructive' if entropy_diff > 0 else 'constructive'})")
    
    void_diff = marx_data['stats']['high_void_count'] - malleus_data['stats']['high_void_count']
    print(f"VOID DELTA: {void_diff:+d} (Marx {'more' if void_diff > 0 else 'less'} void-heavy)")
    
    analysis = {
        'malleus_stats': malleus_data['stats'],
        'marx_stats': marx_data['stats'],
        'entropy_delta': entropy_diff,
        'void_delta': void_diff,
        'interpretation': (
            "Both texts show high deconstructionist entropy. "
            f"Marx's {void_diff:+d} additional void chunks suggests heavier focus on "
            "tearing down without proportional construction."
        )
    }
    
    analysis_path = out_dir / 'cross_document_analysis.json'
    analysis_path.write_text(json.dumps(analysis, indent=2), encoding='utf-8')
    print(f"\n  Saved to {analysis_path}")
    
    return True


if __name__ == '__main__':
    main()
