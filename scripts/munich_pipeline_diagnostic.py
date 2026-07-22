import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configuration
TARGET_DIR = Path(r"E:\munich_handbook_research")
EXPECTED_FILES = {
    "entities": "munich_entities.json",
    "iteration_14_log": "iteration_14.log",
    "iteration_18_artifact": "iteration_18_output.json",
    "intermediate_csv": "chunk_intermediates.csv"
}

class FileIntegrityChecker:
    """Utility class to validate existence and integrity of pipeline artifacts."""

    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.findings: List[Dict[str, str]] = []

    def check_file_existence(self, filename: str) -> Tuple[bool, Optional[Path]]:
        """Check if a specific file exists in the target directory."""
        filepath = self.target_dir / filename
        return filepath.exists(), filepath

    def validate_json_integrity(self, filepath: Path) -> bool:
        """Attempt to parse JSON file to ensure it is not corrupted."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"JSON Integrity Error in {filepath}: {e}")
            return False

    def check_timestamp_consistency(self, filepath: Path) -> bool:
        """Verify file modification time is recent (within last 24h)."""
        if not filepath.exists():
            return False
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        now = datetime.now()
        # Allow 1 hour buffer for writeback latency
        return abs((now - mtime).total_seconds()) < 3600

    def run_diagnostic(self) -> Dict[str, List[Dict]]:
        """Execute full diagnostic suite and return structured findings."""
        results = {
            "missing_files": [],
            "corrupted_artifacts": [],
            "integrity_warnings": []
        }

        for key, filename in EXPECTED_FILES.items():
            exists, filepath = self.check_file_existence(filename)
            
            if not exists:
                results["missing_files"].append({
                    "filename": filename,
                    "expected_path": str(filepath),
                    "severity": "CRITICAL"
                })
            else:
                # Check integrity if file exists
                is_valid_json = self.validate_json_integrity(filepath)
                is_recent = self.check_timestamp_consistency(filepath)

                if not is_valid_json:
                    results["corrupted_artifacts"].append({
                        "filename": filename,
                        "path": str(filepath),
                        "issue": "Invalid JSON structure"
                    })
                elif not is_recent:
                    results["integrity_warnings"].append({
                        "filename": filename,
                        "path": str(filepath),
                        "issue": "Stale file (potential overwrite/corruption)"
                    })

        return results

def generate_report(checker: FileIntegrityChecker) -> str:
    """Generate a human-readable diagnostic report."""
    findings = checker.run_diagnostic()
    
    report_lines = [
        "=" * 60,
        "MUNICH RESEARCH PIPELINE DIAGNOSTIC REPORT",
        f"Generated: {datetime.now().isoformat()}",
        f"Target Directory: {checker.target_dir.absolute()}",
        "=" * 60,
        "",
        "1. MISSING FILES (CRITICAL)",
        "-" * 40
    ]

    if findings["missing_files"]:
        for item in findings["missing_files"]:
            report_lines.append(f"   - {item['filename']}")
            report_lines.append(f"     Path: {item['expected_path']}")
            report_lines.append(f"     Status: NOT FOUND (Iteration 14-18 Error Pattern)")
            report_lines.append("")
    else:
        report_lines.append("   None - All expected files present")
        report_lines.append("")

    report_lines.extend([
        "2. CORRUPTED ARTIFACTS",
        "-" * 40
    ])

    if findings["corrupted_artifacts"]:
        for item in findings["corrupted_artifacts"]:
            report_lines.append(f"   - {item['filename']}")
            report_lines.append(f"     Path: {item['path']}")
            report_lines.append(f"     Issue: {item['issue']}")
            report_lines.append("")
    else:
        report_lines.append("   None - All artifacts valid")
        report_lines.append("")

    report_lines.extend([
        "3. INTEGRITY WARNINGS",
        "-" * 40
    ])

    if findings["integrity_warnings"]:
        for item in findings["integrity_warnings"]:
            report_lines.append(f"   - {item['filename']}")
            report_lines.append(f"     Path: {item['path']}")
            report_lines.append(f"     Issue: {item['issue']}")
            report_lines.append("")
    else:
        report_lines.append("   None - All files have valid timestamps")
        report_lines.append("")

    report_lines.extend([
        "=" * 60,
        "END OF REPORT",
        "=" * 60
    ])

    return "\n".join(report_lines)

if __name__ == "__main__":
    checker = FileIntegrityChecker(TARGET_DIR)
    report = generate_report(checker)
    print(report)