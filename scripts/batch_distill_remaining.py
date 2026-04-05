#!/usr/bin/env python
"""
Batch distillation script for remaining necro chunks.
Distills all missing chunks through the 120B Thinker via batch_distill_source.
Retries failed chunks up to 3 times before marking as permanent failure.
"""
import os
import json
import time
from pathlib import Path
from subprocess import run, PIPE

def check_distilled_chunks(project_dir):
    """Check which necro chunks have already been distilled."""
    distill_dir = Path(project_dir) / 'distillations'
    existing_files = [f for f in os.listdir(distill_dir) if f.startswith('necro_chunk_') and f.endswith('.json')]
    existing_ids = set()
    for f in existing_files:
        try:
            num = int(f.replace('necro_chunk_', '').replace('.json', ''))
            existing_ids.add(num)
        except ValueError:
            continue
    
    all_chunks = set(range(1, 40))
    missing = sorted(all_chunks - existing_ids)
    return list(existing_ids), missing

def validate_json_file(filepath):
    """Validate that a JSON file exists and contains valid spirits array."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if 'spirits' not in data or not isinstance(data['spirits'], list):
            return False, "Missing 'spirits' key"
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, str(e)

def batch_distill_chunk(project_dir, chunk_id):
    """Call batch_distill_source for a specific chunk."""
    cmd = [
        'python', '-m', 'brain',
        '--project-dir', project_dir,
        '--task', 'batch_distill_source',
        '--source-id', 'necro',
        '--chunk-id', str(chunk_id),
        '--goal', 'Extract all spirit names, ranks, functions, appearances, legion counts, conjuration methods, experiment references, and page/folio numbers from Munich Handbook CLM 849 necro section. Also extract experiment descriptions, materials, and ritual procedures.'
    ]
    
    result = run(cmd, capture_output=True, text=True, timeout=300)
    return result.returncode == 0, result.stdout + result.stderr

def main():
    project_dir = r'E:\munich_handbook_research'
    distill_dir = Path(project_dir) / 'distillations'
    
    existing_ids, missing_ids = check_distilled_chunks(project_dir)
    
    print(f"\n{'='*60}")
    print("BATCH DISTILLATION OF NECRO CHUNKS")
    print(f"{'='*60}\n")
    print(f"Existing chunks: {sorted(existing_ids)}")
    print(f"Missing chunks to distill: {missing_ids}")
    print(f"Total chunks remaining: {len(missing_ids)}\n")
    
    if not missing_ids:
        print("All 39 chunks already distilled! Skipping.")
        return
    
    results = {
        'success': [],
        'failed_permanent': [],
        'errors': []
    }
    
    max_retries = 3
    retry_delay = 5  # seconds between retries
    
    for chunk_id in missing_ids:
        print(f"\nProcessing chunk {chunk_id}...")
        filepath = distill_dir / f'necro_chunk_{chunk_id}.json'
        
        if filepath.exists():
            print(f"  Chunk {chunk_id} already exists, skipping.")
            results['success'].append(chunk_id)
            continue
        
        success_count = 0
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            print(f"  Attempt {attempt}/{max_retries}...")
            success, output = batch_distill_chunk(project_dir, chunk_id)
            
            if success:
                # Validate the output file
                valid, error_msg = validate_json_file(filepath)
                if valid:
                    print(f"  ✓ Chunk {chunk_id} distilled successfully!")
                    results['success'].append(chunk_id)
                    break
                else:
                    print(f"  ✗ Distillation succeeded but output invalid: {error_msg}")
                    last_error = error_msg
            else:
                print(f"  ✗ Distillation failed (attempt {attempt}): {output[:200]}")
                last_error = output
            
            if attempt < max_retries:
                time.sleep(retry_delay)
        else:
            # All retries exhausted
            results['failed_permanent'].append(chunk_id)
            results['errors'].append((chunk_id, last_error))
            print(f"  ✗ Chunk {chunk_id} FAILED after {max_retries} attempts")
    
    # Summary report
    print(f"\n{'='*60}")
    print("DISTILLATION SUMMARY")
    print(f"{'='*60}\n")
    print(f"Total chunks processed: {len(missing_ids)}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed permanently: {len(results['failed_permanent'])}")
    
    if results['failed_permanent']:
        print(f"\nFailed chunk IDs: {results['failed_permanent']}")
    
    # Final validation of all 39 chunks
    print(f"\n{'='*60}")
    print("FINAL VALIDATION OF ALL 39 CHUNKS")
    print(f"{'='*60}\n")
    
    all_valid = True
    for chunk_id in range(1, 40):
        filepath = distill_dir / f'necro_chunk_{chunk_id}.json'
        if not filepath.exists():
            print(f"✗ Chunk {chunk_id}: FILE MISSING")
            all_valid = False
        else:
            valid, error_msg = validate_json_file(filepath)
            if valid:
                with open(filepath) as f:
                    data = json.load(f)
                spirit_count = len(data.get('spirits', []))
                print(f"✓ Chunk {chunk_id}: VALID ({spirit_count} spirits extracted)")
            else:
                print(f"✗ Chunk {chunk_id}: INVALID - {error_msg}")
                all_valid = False
    
    if all_valid:
        print(f"\n{'='*60}")
        print("✓ ALL 39 CHUNKS DISTILLED AND VALIDATED SUCCESSFULLY!")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print("✗ SOME CHUNKS FAILED VALIDATION - REVIEW ABOVE")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
