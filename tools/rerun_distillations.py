import os
import json
from argparse import ArgumentParser

def rerun_failed_distillations(manifest_path, output_dir):
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    for chunk in manifest:
        file_name = chunk['file']
        expected_output_file = os.path.join(output_dir, file_name)
        
        if not os.path.exists(expected_output_file) or not chunk.get('success', True):
            print(f"Re-running {expected_output_file}...")
            # Add your retry logic and actual distillation script here
            # For example:
            # result = run_distillation_script(chunk['input'], expected_output_file)
            # if result.success:
            #     chunk['success'] = True

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--manifest', type=str, required=True, help='Path to the manifest file')
    parser.add_argument('--output-dir', type=str, required=True, help='Output directory for distillation results')
    parser.add_argument('--dry-run', action='store_true', help='Dry run: only print what would be done without actually running anything')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.dry_run:
        rerun_failed_distillations(args.manifest, args.output_dir)
    else:
        rerun_failed_distillations(args.manifest, args.output_dir)