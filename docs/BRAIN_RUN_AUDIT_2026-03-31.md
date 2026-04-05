# Brain.py Focus Run Audit — March 30-31, 2026

## Run Parameters
- **Goal**: Munich Handbook × SOM × LGI × QRNG research
- **Iterations**: ~35 (killed at user request)
- **GPU Nodes Used**: All 4 (5090, 4070, A2000, 3060)
- **Target Repo**: `E:\guilford_lattice`

---

## VERDICT SUMMARY

| Category | Status | Notes |
|----------|--------|-------|
| SOM framework | ✅ LEGIT | Custom implementation, runnable |
| Spirit dataset architecture | ✅ LEGIT | Clean class design, extensible |
| QRNG entropy system | ✅ LEGIT | Multi-source entropy, Shannon measurement |
| SOM training stability | ✅ LEGIT | Multi-run validation, convergence logging |
| U-Matrix visualization | ✅ LEGIT | Full viz suite with abyss detection |
| Orchestrator (infernal_topology_analysis.py) | ✅ LEGIT | Ties all modules together |
| Test suite | ✅ LEGIT | Proper unit tests for SOM + QRNG |
| LGI constraint manifold | ⚠️ PARTIAL | Math is correct but `compute_closest_lattice_point()` is a placeholder (returns identity) |
| 11 seed spirits (Table D) | ✅ ACCURATE | Matches user-provided Kieckhefer data exactly |
| 15 "expanded" spirits | ❌ FABRICATED | Hallucinated from general demonology, not from Munich Handbook |
| 150 padding spirits | ❌ FABRICATED | `Spirit_001`–`Spirit_150` with `np.random.uniform()` noise |
| 23 docs/ files | ⚠️ MIXED | Architecture docs are useful; spirit references often cite fabricated names |

---

## LEGITIMATE CODE — Detailed Breakdown

### 1. `src/som_infernal_topology.py` (6.7KB)
**InfernalSOM class** — fully custom SOM, does NOT use MiniSom library:
- `_find_bmu()` — Best Matching Unit via Euclidean distance
- `_radius()` — Neighborhood radius decay schedule
- `_converged()` — Early stopping convergence check
- `train()` — Full training loop with learning rate decay, epoch loss tracking
- `compute_umatrix()` — Proper U-Matrix computation (mean distance to neighbors)
- `visualize_umatrix()` — matplotlib visualization with colorbar, saves PNG
- Also includes `load_munich_handbook_spirits()` (11 real + 10 hallucinated names — see fabrication section)

**Assessment**: Core SOM implementation is solid and runnable. Just needs the spirit loader cleaned up.

### 2. `src/spirit_vectors.py` (7.2KB)
**SpiritDataset class**:
- `add_spirit(name, attributes_dict)` — add spirit with named features
- `normalize_features()` — min-max normalization
- `encode_all()` — convert all spirits to numpy matrix
- `get_spirit_names()`, `get_vector_matrix()` — query methods
- 11 seed spirits loaded with correct 6D vectors:
  - `Rank_Score, Info_Util, Kinetic_Util, Social_Util, Treasure_Util, Legion_Count`

**Assessment**: Clean, extensible architecture. Ready to receive real spirit data.

### 3. `src/qrng_conjuration.py` (8KB)
**QRNGConjuration class**:
- Multi-source entropy: `time.time_ns()`, `os.getpid()`, `secrets.token_bytes()`, SHA-512 mixing
- Optional Qiskit quantum circuit integration (graceful `ImportError` fallback)
- `initialize_som_weights(grid_size)` — generates QRNG-seeded weight matrices
- `measure_entropy(data)` — Shannon entropy measurement
- `validate_randomness(samples)` — chi-square test on generated seeds

**InfernalConjurationProtocol class**:
- `perform_conjuration(spirit_data)` — SOM init + train with QRNG seed
- `conjure_magic_circle_seed(coefficients)` — conservation-checked coefficient generation

**Assessment**: Real, runnable code. Entropy sourcing and validation are correct.

### 4. `src/som_training_stability.py` (9.9KB)
**SOMStabilityValidator class**:
- `run_training(data, seed, epochs)` — single run with controlled seed
- `compute_umatrix_silhouette(som)` — silhouette width from BMU coords
- `log_convergence(som, data)` — tracks QE per epoch, checks monotonic decrease after warmup
- `compute_cluster_centroid_variance(som)` — inter-cluster variance
- `validate_all_runs(data, num_runs, seed_base)` — orchestrates 5 independent runs
- `visualize_convergence(convergence_data)` — plots QE and silhouette curves

**Assessment**: Proper validation framework. Uses sklearn silhouette_score correctly.

### 5. `src/umatrix_visualization.py` (7.2KB)
- `compute_umatrix(som)` — distance between neighboring neurons
- `visualize_umatrix(som)` — pcolormesh with colorbar
- `visualize_umatrix_heatmap(som)` — imshow variant
- `identify_abysses(u_matrix, threshold_percentile=95)` — top-percentile gap detection
- `visualize_som_weights(som)` — weight map visualization
- `analyze_cluster_quality(som, data)` — quantization error, cluster sizes, coverage
- `create_umatrix_report(som, data)` — comprehensive report dict

**Assessment**: Complete visualization pipeline. Abyss detection threshold approach is sound.

### 6. `src/infernal_topology_analysis.py` (16KB)
**InfernalTopologyAnalyzer class** — main orchestrator:
- `initialize(use_qrng)` — loads spirits, normalizes, seeds QRNG
- `train(epochs, learning_rate)` — trains SOM + computes U-Matrix
- `detect_abysses(threshold)` — abyss detection with density metrics
- `analyze_clusters()` — dominant clusters, rank distribution
- `visualize_topology(save_path)` — 4-panel composite figure (U-Matrix, spirit distribution, abyss overlay, rank distribution)
- `generate_topology_report()` — full analysis report
- `_compute_topographic_error()` and `_compute_silhouette_score()` — quality metrics
- `export_results(filepath)` — JSON export

**Assessment**: Good orchestration layer. References `SpiritVectors`, `som_infernal_topology`, and `QrngConjuration` modules. Won't run as-is because import names don't match file class names exactly — needs light wiring fixes.

### 7. `src/lgi_constraint_manifold.py` (3.4KB)
- `constraint_functional(vector, lattice_basis)` — squared distance to nearest lattice point ✅
- `constraint_manifold_distance(vector, lattice_basis)` — perpendicular distance ✅
- `convex_hull_containment_proof_sketch()` — correct mathematical reasoning ✅
- **`compute_closest_lattice_point(vector, lattice_basis)`** — **PLACEHOLDER: returns identity** ❌

**Assessment**: Mathematical framework is correct. Needs actual lattice reduction algorithm (e.g., Babai's nearest plane) to replace the placeholder.

### 8. Test Suite
- `tests/test_som_topology.py` (6KB) — convergence tests, U-Matrix shape tests, uses correct 11 seed spirits
- `tests/test_qrng_conjuration.py` (6.7KB) — QRNG validation, entropy measurement, seed reproducibility
- `src/test_infernal_topology.py` (6KB) — integration tests

**Assessment**: Real tests with correct assertions. Would pass once import wiring is fixed.

### 9. Supporting Files
- `src/spirit_data_loader.py` (9.2KB) — alternate data loader
- `src/convergence_analysis.py` (1.6KB) — convergence utilities
- `src/som_training_utils.py` (3.5KB) — training helpers
- `src/data/spirit_vectors.py` (4.2KB) — data module variant
- `src/utils/quantization_utils.py` (513B) — quantization helpers
- `src/utils/agent_validation.py` (358B) — agent self-check

---

## FABRICATED DATA — What's Wrong

### The 11 Accurate Seed Spirits (from user's prompt / Kieckhefer Table D)
These are **correct** — they match the user-provided data exactly:

| Spirit | Rank | Info | Kinetic | Social | Treasure | Legions |
|--------|------|------|---------|--------|----------|---------|
| Frimost | Duke | 0.6 | 0.8 | 0.3 | 0.2 | 20 |
| Astaroth | King | 0.9 | 0.5 | 0.7 | 0.8 | 40 |
| Surgat | President | 0.4 | 0.3 | 0.2 | 0.9 | 10 |
| Lucifuge | Duke | 0.8 | 0.6 | 0.4 | 0.7 | 30 |
| Agaliarept | Duke | 0.7 | 0.7 | 0.5 | 0.3 | 25 |
| Fleurety | Duke | 0.5 | 0.9 | 0.6 | 0.4 | 15 |
| Sargatanas | Duke | 0.6 | 0.4 | 0.8 | 0.5 | 20 |
| Nebiros | Duke | 0.8 | 0.3 | 0.9 | 0.6 | 35 |
| Bechard | President | 0.3 | 0.5 | 0.7 | 0.8 | 12 |
| Guland | President | 0.7 | 0.8 | 0.3 | 0.4 | 18 |
| Sustugriel | Duke | 0.5 | 0.6 | 0.4 | 0.7 | 22 |

### The 15 "Expanded" Spirits — HALLUCINATED
Found in `load_munich_handbook_spirits()` and some `spirit_vectors.py` variants. **Not from the Munich Handbook**:
- **Goetia/general demonology**: Beelzebub, Lucifer, Asmodeus, Buer, Gamygyn, Ose
- **Egyptian mythology**: Khepri, Seshat
- **Pop culture**: "Ghidorah" (King Ghidorah from Godzilla)
- **German-sounding fabrications**: Auer, Baldur, Cernus, Dagobert, Eisenhart, Falk

### The 150 Padding Spirits — PURE NOISE
`Spirit_001` through `Spirit_150` generated with `np.random.uniform()` — random vectors with no meaning.

### Root Cause
The local LLMs cannot access Archive.org or the actual Munich Handbook text. They only had the 11 seed spirits from the user's prompt and hallucinated the rest from general knowledge + random generation.

---

## WHAT TO DO NEXT

1. **Provide real spirit data**: Extract all spirits from Kieckhefer's book manually or from a digitized source. Create a `spirits.json` or `spirits.csv` with the 6D feature vectors.
2. **Replace fabricated data**: Swap out `load_munich_handbook_spirits()` and the ADDITIONAL_SPIRITS dict with real data. The SpiritDataset class is ready for this.
3. **Fix closest lattice point**: Replace the identity placeholder in `lgi_constraint_manifold.py` with Babai's nearest plane algorithm or similar.
4. **Fix import wiring**: The orchestrator (`infernal_topology_analysis.py`) references class names that don't match the actual exports. Light fix needed.
5. **Re-run brain.py** with real data loaded into the repo — the framework will produce meaningful topology results.
6. **Bridge to harmonic-field-consciousness**: Not yet started.

---

## FILE MANIFEST (new files from this run, Mar 30-31 2026)

### Root
- `som_infernal_topology.py`, `qrng_conjuration.py`, `som_validation.py`
- `consciousness_metrics.py`, `chaos_analysis.py`, `lgi_constraint_manifold.py`
- `spirit_vectors.py`, `main.py`, `.progress.py`
- `requirements.txt`, `README.md`

### src/
- `som_infernal_topology.py`, `spirit_vectors.py`, `lgi_constraint_manifold.py`
- `qrng_conjuration.py`, `som_training_stability.py`, `infernal_topology_analysis.py`
- `umatrix_visualization.py`, `spirit_data_loader.py`, `convergence_analysis.py`
- `som_training_utils.py`, `test_infernal_topology.py`, `__init__.py`
- `data/spirit_vectors.py`, `utils/quantization_utils.py`, `utils/agent_validation.py`

### tests/
- `test_som_topology.py`, `test_qrng_conjuration.py`

### docs/ (23 files)
- Architecture, research reports, progress reports, missing spirits analysis
- SOM testing workflow, validation metrics, U-Matrix analysis
- Spirit vector audit, expansion proposals, research context
