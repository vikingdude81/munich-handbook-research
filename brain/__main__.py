import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path so we can find 'tools' and 'config'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from tools.source_distill import DistillSourceChunk
except ImportError as e:
    print(f"Error importing tools.source_distill: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Brain: Orchestrator for Munich Handbook Research")
    parser.add_argument("--project-dir", required=True, help="Path to project root")
    parser.add_argument("--task", required=True, help="Task to perform (e.n. batch_distill_source)")
    parser.add_argument("--source-id", required=False, help="ID of the source text (e.g., 'necro')")
    parser.add_argument("--chunk-id", required=False, type=int, help="ID of the chunk to process")
    parser.add_argument("--goal", required=False, help="Goal for distillation")

    args = parser.parse_args()

    if args.task == "batch_distill_source":
        if not args.source_id or args.chunk_id is None or not args.goal:
            print("Error: batch_distill_source requires --source-id, --chunk-id, and --goal")
            sys.exit(1)

        # Prepare output directory and path
        project_path = Path(args.project_dir).resolve()
        distill_dir = project_path / "distillations"
        distill_dir.mkdir(parents=True, exist_ok=True)
        output_file = distill_dir / f"{args.source_id}_chunk_{args.chunk_id}.json"

        print(f"[*] Starting task: {args.task}")
        print(f"[*] Source: {args.source_id}, Chunk: {args.chunk_id}")
        print(f"[*] Target output: {output_file}")

        try:
            tool = DistillSourceChunk()
            
            # The tool expects a dictionary of parameters as seen in our previous test
            params = {
                "project_dir": str(project_path),
                "source_id": args.source_id,
                "chunk_id": args.chunk_id,
                "goal": args.goal
            }

            print("[*] Calling DistillSourceChunk tool...")
            result = tool.call(params)
            
            # The result is a dictionary containing the extracted entities/summary
            # We need to write this as JSON to the expected file path
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"[+] Successfully wrote distillation result to {output_file}")
            sys.exit(0)

        except Exception as e:
            print(f"[-] Task failed with error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print(f"[-] Unknown task: {args.task}")
        sys.exit(1)

if __name__ == "__main__":
    main()
