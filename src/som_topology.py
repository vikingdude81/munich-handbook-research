"""
SOM Infernal Topology — Self-Organizing Map for spirit clustering.

Trains a MiniSom on spirit vectors to reveal clusters ("Infernal Courts")
and the Abysses (high-distance U-Matrix regions) between incompatible
magical operations.
"""

import json
import os
import numpy as np
from minisom import MiniSom
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from collections import Counter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "som_output")


def train_som(spirits_data, spirit_names=None, shape=(15, 15),
              learning_rate=0.5, sigma=2.5, num_iteration=2000,
              use_epochs=True):
    """
    Train a SOM on spirit vectors.

    Args:
        spirits_data: (n_spirits, n_features) numpy array
        spirit_names: optional list of names for labelling
        shape: (rows, cols) grid size
        learning_rate: initial learning rate
        sigma: initial neighbourhood radius
        num_iteration: epochs if use_epochs else raw sample draws
        use_epochs: when True, num_iteration counts FULL passes over the data.
            Previously the code called train_random(data, 2000), which draws
            2000 random samples total — only ~1.6 passes over 1,254 spirits, not
            "2000 epochs" as the README claimed. train(use_epochs=True) makes the
            count mean what the docs say.

    Returns:
        Trained MiniSom instance
    """
    n_features = spirits_data.shape[1]
    som = MiniSom(shape[0], shape[1], n_features,
                  sigma=sigma, learning_rate=learning_rate,
                  random_seed=42)

    # PCA initialization for better convergence
    som.pca_weights_init(spirits_data)
    som.train(spirits_data, num_iteration, use_epochs=use_epochs, verbose=True)
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
    out = {}
    for k, v in sorted(clusters.items()):
        out[f"{k[0]},{k[1]}"] = {"count": len(v), "spirits": v}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


def plot_u_matrix(som, clusters, filepath):
    """Plot the U-Matrix heatmap with spirit density overlay."""
    u_matrix = som.distance_map()
    rows, cols = u_matrix.shape

    fig, ax = plt.subplots(figsize=(12, 12))
    im = ax.imshow(u_matrix, cmap="bone_r", interpolation="nearest", origin="lower")
    plt.colorbar(im, ax=ax, label="U-Matrix Distance (Abyss Depth)")

    # Overlay spirit count as circles
    for (r, c), names in clusters.items():
        size = min(len(names), 30)
        ax.plot(c, r, "o", color="crimson", markersize=3 + size * 0.8,
                alpha=0.6)
        if len(names) >= 8:
            ax.annotate(str(len(names)), (c, r), ha="center", va="center",
                        fontsize=7, color="white", fontweight="bold")

    ax.set_title("Infernal Topology — U-Matrix with Spirit Density", fontsize=14)
    ax.set_xlabel("SOM Column")
    ax.set_ylabel("SOM Row")
    fig.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    print(f"  Saved U-Matrix: {filepath}")


def plot_feature_planes(som, feature_labels, filepath):
    """Plot component planes for each feature dimension."""
    weights = som.get_weights()  # (rows, cols, n_features)
    n_features = weights.shape[2]
    ncols = 7
    nrows = (n_features + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 2.5, nrows * 2.5))
    axes = axes.flatten()

    for i in range(n_features):
        ax = axes[i]
        plane = weights[:, :, i]
        im = ax.imshow(plane, cmap="viridis", interpolation="nearest", origin="lower")
        ax.set_title(feature_labels[i], fontsize=7)
        ax.set_xticks([])
        ax.set_yticks([])

    # Hide unused axes
    for j in range(n_features, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Component Planes — Feature Activation Across SOM Grid", fontsize=12)
    fig.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    print(f"  Saved component planes: {filepath}")


def plot_hit_map(som, spirits_data, spirit_names, filepath):
    """Frequency histogram — how many spirits land in each cell."""
    rows, cols = som.get_weights().shape[:2]
    hit_map = np.zeros((rows, cols))
    for vec in spirits_data:
        r, c = som.winner(vec)
        hit_map[r, c] += 1

    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(hit_map, cmap="YlOrRd", interpolation="nearest", origin="lower")
    plt.colorbar(im, ax=ax, label="Spirit Count")
    ax.set_title("Hit Map — Spirit Density per Cell", fontsize=14)
    ax.set_xlabel("SOM Column")
    ax.set_ylabel("SOM Row")
    fig.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    print(f"  Saved hit map: {filepath}")


def label_courts(clusters, som, spirits_data, spirit_names, feature_labels):
    """
    Label each populated SOM cell with a dominant function/nature tag
    to name the 'Infernal Courts'.
    """
    weights = som.get_weights()
    court_labels = {}

    # Function feature indices (12..21) and nature indices (22..24)
    func_names = feature_labels[12:22]
    nature_names = feature_labels[22:25]

    for cell, names in clusters.items():
        r, c = cell
        w = weights[r, c]
        # Dominant function
        func_activations = w[12:22]
        nature_activations = w[22:25]

        top_func_idx = np.argmax(func_activations)
        top_func = func_names[top_func_idx] if func_activations[top_func_idx] > 0.3 else "mixed"

        top_nat_idx = np.argmax(nature_activations)
        top_nature = nature_names[top_nat_idx] if nature_activations[top_nat_idx] > 0.3 else "neutral"

        court_labels[cell] = {
            "court_name": f"{top_nature}_{top_func}",
            "dominant_function": top_func,
            "dominant_nature": top_nature,
            "population": len(names),
            "notable_spirits": names[:5],
        }
    return court_labels


def run_full_pipeline():
    """Execute the complete SOM training and visualization pipeline."""
    from src.spirit_vectors import load_seed_spirits, get_feature_labels

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load and vectorize. require_attributes=True drops the ~70% single-mention,
    # zero-attribute records that otherwise collapse into one node and produce the
    # spurious "Unnamed Host" mega-cluster + misleadingly low QE/TE.
    print("Loading spirit vectors...")
    data_all, names_all = load_seed_spirits()
    data, names = load_seed_spirits(require_attributes=True)
    feature_labels = get_feature_labels()
    print(f"  {len(names)} attributed spirits (filtered from {len(names_all)} total), "
          f"{data.shape[1]} features")

    # Normalize features to [0, 1] for SOM
    col_max = data.max(axis=0)
    col_max[col_max == 0] = 1.0  # avoid division by zero
    data_norm = data / col_max

    # Train
    EPOCHS = 2000
    print(f"\nTraining SOM (15×15, {EPOCHS} epochs)...")
    som = train_som(data_norm, names, shape=(15, 15),
                    num_iteration=EPOCHS, use_epochs=True)

    # Metrics
    qe, te = compute_qe_te(som, data_norm)
    print(f"\n  Quantization Error: {qe:.4f}")
    print(f"  Topographic Error:  {te:.4f}")

    # Cluster assignments
    clusters = get_cluster_assignments(som, data_norm, names)
    populated = len(clusters)
    sizes = [len(v) for v in clusters.values()]
    print(f"\n  Populated cells: {populated}/225")
    print(f"  Cluster sizes: min={min(sizes)}, max={max(sizes)}, "
          f"mean={np.mean(sizes):.1f}, median={np.median(sizes):.1f}")

    # Exports
    clusters_path = os.path.join(OUTPUT_DIR, "cluster_assignments.json")
    export_clusters_json(clusters, clusters_path)
    print(f"  Saved clusters: {clusters_path}")

    # Court labels
    court_labels = label_courts(clusters, som, data_norm, names, feature_labels)
    courts_path = os.path.join(OUTPUT_DIR, "infernal_courts.json")
    courts_out = {f"{k[0]},{k[1]}": v for k, v in sorted(court_labels.items())}
    with open(courts_path, "w", encoding="utf-8") as f:
        json.dump(courts_out, f, indent=2, ensure_ascii=False)
    print(f"  Saved court labels: {courts_path}")

    # Visualizations
    print("\nGenerating visualizations...")
    plot_u_matrix(som, clusters, os.path.join(OUTPUT_DIR, "u_matrix.png"))
    plot_feature_planes(som, feature_labels, os.path.join(OUTPUT_DIR, "component_planes.png"))
    plot_hit_map(som, data_norm, names, os.path.join(OUTPUT_DIR, "hit_map.png"))

    # Metrics summary
    metrics = {
        "n_spirits": len(names),
        "n_features": data.shape[1],
        "grid_shape": [15, 15],
        "epochs": EPOCHS,
        "training": "som.train(use_epochs=True) — full passes over the data",
        "caveat": (
            "~70% of spirit vectors are single-occurrence and ~145 have zero "
            "attributes, so their vectors are near-identical near-zero points. "
            "The dominant 'Unnamed Host' mega-cluster is largely this null bucket, "
            "and the very low QE/TE partly reflect that degeneracy rather than "
            "meaningful topology. Filter to attributed spirits before treating "
            "clusters as 'courts'."
        ),
        "quantization_error": round(qe, 4),
        "topographic_error": round(te, 4),
        "populated_cells": populated,
        "total_cells": 225,
        "cluster_size_min": min(sizes),
        "cluster_size_max": max(sizes),
        "cluster_size_mean": round(np.mean(sizes), 2),
        "top_10_courts": sorted(
            [(k, len(v)) for k, v in clusters.items()],
            key=lambda x: -x[1]
        )[:10],
    }
    metrics["top_10_courts"] = [
        {"cell": f"{c[0]},{c[1]}", "count": cnt}
        for (c, cnt) in metrics["top_10_courts"]
    ]
    metrics_path = os.path.join(OUTPUT_DIR, "som_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Saved metrics: {metrics_path}")

    print("\n=== SOM Pipeline Complete ===")
    return som, clusters, court_labels, metrics


if __name__ == "__main__":
    run_full_pipeline()
