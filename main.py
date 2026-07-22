"""
Munich Handbook Research — Main entry point.

Thin launcher for the SOM Infernal Topology pipeline. The previous version
imported names that never existed (`FEATURE_NAMES`, `get_spirit_objects`) and
called `train_som(epochs=...)` after that kwarg was renamed — it could not run.
This delegates to the real, maintained pipeline in `src/som_topology.py`.

Usage:
    python main.py            # run the full SOM pipeline (writes som_output/)
    python main.py --manifold # also compute the LGI manifold diagnostic
"""

import argparse
import os
import sys

# Ensure repo root is importable as a package root (`src` is a package).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description="Munich Handbook SOM topology")
    ap.add_argument("--manifold", action="store_true",
                    help="also run the LGI Magic Circle manifold diagnostic")
    args = ap.parse_args()

    print("=" * 60)
    print("MUNICH HANDBOOK INFERNAL TOPOLOGY")
    print("=" * 60)

    from src.som_topology import run_full_pipeline
    som, clusters, court_labels, metrics = run_full_pipeline()

    print(f"\nSpirits: {metrics['n_spirits']} | features: {metrics['n_features']}")
    print(f"QE={metrics['quantization_error']} TE={metrics['topographic_error']} "
          f"| populated {metrics['populated_cells']}/{metrics['total_cells']}")

    if args.manifold:
        print("\n--- LGI Magic Circle Manifold ---")
        from src.spirit_vectors import load_seed_spirits
        from src.lgi_manifold import MagicCircleManifold
        data, names = load_seed_spirits()
        manifold = MagicCircleManifold(data)
        print(f"Lattice volume: {manifold.lattice_volume():.4f}")
        print(f"Basis shape:    {manifold.basis.shape}")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
