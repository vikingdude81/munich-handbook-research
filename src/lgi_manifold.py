"""
LGI Constraint Manifold — the Magic Circle, redesigned.

The previous implementation projected onto the real linear span of ALL spirit
vectors. With 1,100+ spirits in 28 dimensions that span is the whole space, so
`is_within_circle()` was True for every input — the circle admitted everything.
(See docs/APPS_MAPPING_AUDIT.md §2.)

This redesign keeps the metaphor honest in two complementary forms:

1. MagicCircleManifold — the classic circle: a SMALL curated seed set of
   archetypal spirits (default: the commander tier — Astaroth, Belial, Berith,
   Lucifer, Paimon, Beelzebub, Oriens, Satan). Nine vectors span a genuine
   9-D subspace of R^28, so projection residual is a meaningful distance:
   "how far is this configuration from the plane defined by the inscribed
   names?" The circle inscribed with few chosen names — as on the vellum.

2. MahalanobisCircle — the statistical circle for the full corpus: fits a
   regularized Gaussian to all attributed spirit vectors and tests membership
   by Mahalanobis distance against a chi-square quantile. "Is this
   configuration within the distribution of known spirits?"
"""

import json
import os

import numpy as np
from scipy.linalg import qr
from scipy.stats import chi2

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIFIED_DB = os.path.join(_ROOT, "data", "unified_entities.json")

# The commander tier — the names inscribed on the circle by default.
DEFAULT_SEED_NAMES = [
    "astaroth", "belial", "berith", "lucifer",
    "paimon", "beelzebub", "oriens", "satan",
]


# ──────────────────────────────────────────────────────────────────────────────
# 1. The curated seed circle
# ──────────────────────────────────────────────────────────────────────────────
class MagicCircleManifold:
    """
    Subspace manifold spanned by a small curated seed set (n_seeds << n_features).

    residual(v)          — distance from v to the seed subspace
    is_within_circle(v)  — residual <= radius. If radius is None it is
                           calibrated at construction as the q-quantile of the
                           corpus residual distribution (requires corpus).
    """

    def __init__(self, seed_vectors, seed_names=None, radius=None,
                 corpus=None, calibration_q=0.25):
        self.seed_vectors = np.array(seed_vectors, dtype=float)
        if self.seed_vectors.ndim != 2:
            raise ValueError("seed_vectors must be (n_seeds, n_features)")
        n_seeds, n_features = self.seed_vectors.shape
        if n_seeds >= n_features:
            raise ValueError(
                f"{n_seeds} seeds in {n_features}-D span (nearly) the whole "
                "space — the circle would admit everything. Use a small "
                "curated seed set (or MahalanobisCircle for corpus-scale).")
        self.seed_names = list(seed_names or [])
        Q, _ = qr(self.seed_vectors.T, mode="economic")
        self.basis = Q  # (n_features, n_seeds)

        if radius is not None:
            self.radius = float(radius)
        elif corpus is not None:
            res = np.array([self.residual(v) for v in np.asarray(corpus)])
            self.radius = float(np.quantile(res, calibration_q))
        else:
            self.radius = 0.5  # documented fallback; prefer calibration

    def project(self, vector):
        v = np.asarray(vector, dtype=float)
        return self.basis @ (self.basis.T @ v)

    def residual(self, vector):
        v = np.asarray(vector, dtype=float)
        return float(np.linalg.norm(v - self.project(v)))

    def is_within_circle(self, vector):
        return self.residual(vector) <= self.radius

    def lattice_volume(self):
        """sqrt(det Gram) of the seed set — meaningful for independent seeds."""
        G = self.seed_vectors @ self.seed_vectors.T
        return float(np.sqrt(max(np.linalg.det(G), 0.0)))

    def shortest_vector_approx(self, coeff_range=range(-2, 3), max_seeds=12):
        """Brute-force shortest nonzero lattice vector (feasible for small n)."""
        from itertools import product
        n = self.seed_vectors.shape[0]
        if n > max_seeds:
            raise ValueError(f"brute force infeasible for {n} seeds (> {max_seeds})")
        best_norm, best_vec = np.inf, None
        for coeffs in product(coeff_range, repeat=n):
            if not any(coeffs):
                continue
            v = np.tensordot(coeffs, self.seed_vectors, axes=1)
            norm = np.linalg.norm(v)
            if norm < best_norm:
                best_norm, best_vec = norm, v
        return best_vec, float(best_norm)


# ──────────────────────────────────────────────────────────────────────────────
# 2. The statistical circle (corpus-scale membership)
# ──────────────────────────────────────────────────────────────────────────────
class MahalanobisCircle:
    """
    Membership by Mahalanobis distance to the attributed-spirit distribution.

    is_within(v, p=0.95) — True if v lies inside the p-mass chi-square ellipsoid
    of the fitted (regularized) Gaussian.
    """

    def __init__(self, corpus, ridge=1e-3):
        X = np.asarray(corpus, dtype=float)
        self.mean = X.mean(axis=0)
        cov = np.cov(X, rowvar=False)
        cov += np.eye(cov.shape[0]) * ridge  # regularize near-singular dims
        self.cov_inv = np.linalg.inv(cov)
        self.dof = X.shape[1]

    def distance(self, vector):
        d = np.asarray(vector, dtype=float) - self.mean
        return float(np.sqrt(d @ self.cov_inv @ d))

    def is_within(self, vector, p=0.95):
        return self.distance(vector) ** 2 <= chi2.ppf(p, df=self.dof)


# ──────────────────────────────────────────────────────────────────────────────
# Loading helpers
# ──────────────────────────────────────────────────────────────────────────────
def load_seed_circle(db_path=None, seed_names=None):
    """Build the default commander-tier circle, radius-calibrated on the corpus."""
    from src.spirit_vectors import load_seed_spirits, vectorize_spirit

    db_path = db_path or UNIFIED_DB
    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)
    wanted = set(seed_names or DEFAULT_SEED_NAMES)
    seeds, names = [], []
    for e in db["entities"]:
        if e.get("type") == "spirit" and e.get("canonical_name") in wanted:
            seeds.append(vectorize_spirit(e))
            names.append(e["canonical_name"])
    if len(seeds) < 3:
        raise RuntimeError(f"only found {len(seeds)} of the seed spirits in DB")
    corpus, _ = load_seed_spirits(db_path, require_attributes=True)
    circle = MagicCircleManifold(seeds, names, corpus=corpus)
    return circle, corpus


if __name__ == "__main__":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    sys.path.insert(0, _ROOT)

    circle, corpus = load_seed_circle()
    print(f"Seed circle: {len(circle.seed_names)} inscribed names: "
          f"{', '.join(circle.seed_names)}")
    print(f"Subspace dim: {circle.basis.shape[1]} of {circle.basis.shape[0]}")
    print(f"Calibrated radius (q25 of corpus residuals): {circle.radius:.4f}")
    print(f"Lattice volume: {circle.lattice_volume():.4f}")

    res = np.array([circle.residual(v) for v in corpus])
    inside = int((res <= circle.radius).sum())
    print(f"\nCorpus residuals: min={res.min():.4f} median={np.median(res):.4f} "
          f"max={res.max():.4f}")
    print(f"Within the circle: {inside}/{len(corpus)} attributed spirits "
          f"({100*inside/len(corpus):.1f}%) — a discriminating boundary, "
          "not a vacuous one")

    # Sanity: the seeds themselves must be inside (residual ~ 0)
    seed_res = [circle.residual(v) for v in circle.seed_vectors]
    print(f"Seed self-residuals (should be ~0): max={max(seed_res):.2e}")

    # Random noise should be OUTSIDE
    rng = np.random.default_rng(42)
    noise = rng.random(circle.basis.shape[0])
    print(f"Random vector: residual={circle.residual(noise):.4f} "
          f"in_circle={circle.is_within_circle(noise)}")

    maha = MahalanobisCircle(corpus)
    d_typical = np.median([maha.distance(v) for v in corpus[:200]])
    print(f"\nMahalanobis circle: median corpus distance={d_typical:.2f}, "
          f"noise distance={maha.distance(noise):.2f}, "
          f"noise within 95% ellipsoid: {maha.is_within(noise)}")
