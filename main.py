"""
Munich Handbook Research — Main entry point.

Loads verified spirit vectors, trains the SOM topology, and computes the
LGI constraint manifold.  Prints a diagnostic report.
"""

import sys
import os

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from spirit_vectors import load_seed_spirits, FEATURE_NAMES, get_spirit_objects
from som_topology import train_som, get_u_matrix, compute_qe_te, get_cluster_assignments
from lgi_manifold import MagicCircleManifold

import numpy as np


def main():
    print("=" * 60)
    print("MUNICH HANDBOOK INFERNAL TOPOLOGY")
    print("=" * 60)

    # --- Load verified seed spirits ---
    data, names = load_seed_spirits()
    print(f"\nVerified spirits: {len(names)}")
    print(f"Feature space:    {FEATURE_NAMES}")
    print(f"Data shape:       {data.shape}\n")

    for s in get_spirit_objects():
        print(f"  {s.name:12s}  rank={s.rank:10s}  fn={s.function:12s}  v={s.vector}")

    # --- SOM Infernal Topology ---
    print("\n--- SOM Training ---")
    som = train_som(data, names, shape=(4, 4), epochs=1000)
    qe, te = compute_qe_te(som, data)
    print(f"Quantization Error: {qe:.4f}")
    print(f"Topographic Error:  {te:.4f}")

    clusters = get_cluster_assignments(som, data, names)
    print("\nCluster assignments:")
    for cell, spirits in sorted(clusters.items()):
        print(f"  Cell {cell}: {', '.join(spirits)}")

    # --- LGI Constraint Manifold ---
    print("\n--- LGI Magic Circle Manifold ---")
    manifold = MagicCircleManifold(data)
    print(f"Lattice volume:  {manifold.lattice_volume():.4f}")
    print(f"Basis shape:     {manifold.basis.shape}")

    # Test each spirit's residual (should be ~0 since they define the lattice)
    print("\nSpirit residuals (distance to manifold):")
    for i, name in enumerate(names):
        r = manifold.residual(data[i])
        print(f"  {name:12s}  residual={r:.6f}  in_circle={manifold.is_within_circle(data[i])}")

    print("\n" + "=" * 60)
    print("DONE — Run brain.py focus mode to expand with source texts")
    print("=" * 60)


if __name__ == "__main__":
    main()
