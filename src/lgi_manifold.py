"""
LGI Constraint Manifold — Lattice-Governed Inference for spirit vectors.

The Magic Circle = Constraint Manifold = Lattice L = {sum(a_i * v_i) | a_i in Z}
This module computes lattice bases from spirit vectors and tests whether
new spirit configurations lie within the manifold defined by the seed data.
"""

import numpy as np
from typing import Tuple
from scipy.linalg import qr


class MagicCircleManifold:
    """
    The Magic Circle as a lattice constraint manifold.

    Given spirit vectors v_1..v_n, the lattice is:
        L = { sum(a_i * v_i) | a_i in Z }
    A configuration is "within the circle" if it can be expressed
    as an integer linear combination of the basis vectors.
    """

    def __init__(self, spirits_data: np.ndarray, radius: float = 7.0):
        self.spirits_data = np.array(spirits_data, dtype=float)
        self.n_spirits, self.n_features = self.spirits_data.shape
        self.radius = radius
        self.basis = self._compute_basis()

    def _compute_basis(self) -> np.ndarray:
        """QR-based orthogonal basis from spirit vectors."""
        Q, R = qr(self.spirits_data.T, mode='economic')
        return Q

    def project(self, vector: np.ndarray) -> np.ndarray:
        """Project a vector onto the lattice subspace."""
        return self.basis @ (self.basis.T @ vector)

    def residual(self, vector: np.ndarray) -> float:
        """Distance from vector to its projection on the manifold."""
        proj = self.project(vector)
        return float(np.linalg.norm(vector - proj))

    def is_within_circle(self, vector: np.ndarray) -> bool:
        """Check if a vector lies within the Magic Circle radius."""
        return self.residual(vector) <= self.radius

    def lattice_volume(self) -> float:
        """Compute the fundamental domain volume (det of Gram matrix)."""
        G = self.spirits_data @ self.spirits_data.T
        return float(np.sqrt(abs(np.linalg.det(G))))

    def shortest_vector_approx(self) -> Tuple:
        """Approximate shortest lattice vector (brute-force for small n)."""
        from itertools import product
        best_norm = np.inf
        best_vec = None
        coeff_range = range(-2, 3)
        for coeffs in product(coeff_range, repeat=self.n_spirits):
            if all(c == 0 for c in coeffs):
                continue
            v = sum(c * self.spirits_data[i] for i, c in enumerate(coeffs))
            n = np.linalg.norm(v)
            if n < best_norm:
                best_norm = n
                best_vec = v
        return best_vec, best_norm


if __name__ == "__main__":
    from spirit_vectors import load_seed_spirits
    data, names = load_seed_spirits()
    m = MagicCircleManifold(data)
    print(f"Lattice volume: {m.lattice_volume():.4f}")
    print(f"Basis shape: {m.basis.shape}")
    test = np.random.rand(6)
    print(f"Random vector in circle? {m.is_within_circle(test)}  (residual={m.residual(test):.4f})")
