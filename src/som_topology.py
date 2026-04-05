"""
SOM Infernal Topology — Self-Organizing Map for spirit clustering.

Trains a MiniSom on spirit vectors to reveal clusters ("Infernal Courts")
and the Abysses (high-distance U-Matrix regions) between incompatible
magical operations.
"""

import json
import numpy as np
from minisom import MiniSom


def seed_som_weights(som, shape, n_features=6):
    """Initialize SOM weights with random values in the spirit vector space."""
    rng = np.random.default_rng()
    weights = rng.uniform(0, 1, (shape[0], shape[1], n_features))
    som._weights = weights


def train_som(spirits_data, spirit_names=None, shape=(5, 5),
              learning_rate=0.5, sigma=1.0, epochs=500):
    """
    Train a SOM on spirit vectors.

    Args:
        spirits_data: (n_spirits, n_features) numpy array
        spirit_names: optional list of names for labelling
        shape: (rows, cols) grid size
        learning_rate: initial learning rate
        sigma: initial neighbourhood radius
        epochs: training iterations

    Returns:
        Trained MiniSom instance
    """
    n_features = spirits_data.shape[1]
    som = MiniSom(shape[0], shape[1], n_features,
                  sigma=sigma, learning_rate=learning_rate,
                  random_seed=42)

    # Initialize and train
    som.random_weights_init(spirits_data)
    som.train_random(spirits_data, epochs)
    return som


def get_u_matrix(som):
    """Compute the U-Matrix (unified distance matrix)."""
    return som.distance_map()


def get_cluster_assignments(som, spirits_data, spirit_names):
    """
    Map each spirit to its Best Matching Unit (BMU) on the SOM grid.

    Returns:
        dict: {(row, col): [spirit_names_in_this_cell]}
    """
    clusters = {}
    for i, vec in enumerate(spirits_data):
        bmu = som.winner(vec)
        clusters.setdefault(bmu, []).append(spirit_names[i])
    return clusters


def compute_qe_te(som, spirits_data):
    """Quantization Error and Topographic Error."""
    qe = som.quantization_error(spirits_data)
    te = som.topographic_error(spirits_data)
    return qe, te


def export_clusters_json(clusters, filepath):
    """Save cluster assignments to JSON (keys converted to strings)."""
    out = {f"{k[0]},{k[1]}": v for k, v in clusters.items()}
    with open(filepath, "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    from spirit_vectors import load_seed_spirits
    data, names = load_seed_spirits()
    print(f"Training SOM on {len(names)} spirits ...")
    som = train_som(data, names)
    qe, te = compute_qe_te(som, data)
    print(f"QE={qe:.4f}  TE={te:.4f}")
    clusters = get_cluster_assignments(som, data, names)
    for cell, spirits in sorted(clusters.items()):
        print(f"  Cell {cell}: {spirits}")
