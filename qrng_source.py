"""
qrng_source.py — Quantum Random Number Generation source module.

Provides true quantum entropy for seeding inference runs, scheduling,
and experimental context injection. Maps to the Munich Handbook's use
of astronomical timing and "true" cosmic randomness for ritual timing.

The Munich Handbook's practitioners relied on astronomical tables and
planetary cycles as sources of "objective" timing — not fabricated by
the practitioner, but observed from the cosmos. QRNG is the modern
equivalent: entropy that comes from outside the deterministic system.

Backends (in priority order):
  1. ANU QRNG API (https://qrng.anu.edu.au) — Australian National University
  2. NIST Randomness Beacon — NIST quantum beacon
  3. os.urandom() fallback — CSPRNG if quantum sources unavailable

Usage:
    from qrng_source import get_quantum_seed, get_quantum_float, get_quantum_bytes, QRNGSource

    seed = get_quantum_seed()           # integer seed
    val  = get_quantum_float()          # float in [0.0, 1.0)
    raw  = get_quantum_bytes(n=8)       # raw bytes
    src  = QRNGSource()
    src.get_seed(n_bytes=4)
"""

import os
import json
import logging
import time
import datetime
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# QRNGLog — provenance record for each draw
# ---------------------------------------------------------------------------

@dataclass
class QRNGLog:
    """Provenance record for a single QRNG draw."""
    timestamp: str
    seed: int
    source: str
    n_bytes: int


def save_qrng_log(log_entry: QRNGLog, path: str = "logs/qrng_log.jsonl") -> None:
    """Append a QRNG log entry to the JSONL audit trail."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(log_entry)) + "\n")


# ---------------------------------------------------------------------------
# QRNGSource — multi-backend quantum entropy source
# ---------------------------------------------------------------------------

class QRNGSource:
    """
    Multi-backend QRNG source.

    Tries backends in priority order:
      1. ANU QRNG REST API
      2. NIST Randomness Beacon v2.0
      3. os.urandom() CSPRNG fallback

    Attributes:
        source_name: Name of the backend that last successfully provided entropy.
    """

    ANU_URL = "https://qrng.anu.edu.au/API/jsonI.php?length={n}&type=uint8"
    NIST_URL = "https://beacon.nist.gov/beacon/2.0/pulse/last"

    def __init__(self, timeout: int = 5):
        self._timeout = timeout
        self._last_source: str = "uninitialized"

    @property
    def source_name(self) -> str:
        """Name of the backend that provided the most recent entropy."""
        return self._last_source

    # ------------------------------------------------------------------
    # Private backend methods
    # ------------------------------------------------------------------

    def _fetch_anu(self, n: int) -> Optional[bytes]:
        """Fetch n random bytes from the ANU QRNG REST API."""
        try:
            import requests  # lazy import so module loads without requests
            url = self.ANU_URL.format(n=n)
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()
            if data.get("success") and "data" in data:
                return bytes(data["data"][:n])
            logger.warning("ANU QRNG: unexpected response format")
            return None
        except Exception as exc:
            logger.info("ANU QRNG unavailable: %s", exc)
            return None

    def _fetch_nist(self, n: int) -> Optional[bytes]:
        """Fetch entropy from the NIST Randomness Beacon v2.0."""
        try:
            import requests
            response = requests.get(self.NIST_URL, timeout=self._timeout)
            response.raise_for_status()
            pulse = response.json().get("pulse", {})
            output_hex = pulse.get("outputValue", "")
            if not output_hex:
                logger.warning("NIST Beacon: no outputValue in response")
                return None
            raw = bytes.fromhex(output_hex)
            # NIST pulse is 64 bytes; cycle if more are needed
            result = bytearray()
            while len(result) < n:
                result.extend(raw)
            return bytes(result[:n])
        except Exception as exc:
            logger.info("NIST Beacon unavailable: %s", exc)
            return None

    def _fetch_local(self, n: int) -> bytes:
        """Fall back to os.urandom() (CSPRNG)."""
        logger.info("Using os.urandom() CSPRNG fallback for %d bytes", n)
        return os.urandom(n)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_bytes(self, n: int = 4) -> bytes:
        """
        Return n random bytes from the highest-priority available backend.

        Args:
            n: Number of bytes to return (>0).

        Returns:
            Bytes object of length n.
        """
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")

        result = self._fetch_anu(n)
        if result is not None:
            self._last_source = "anu_qrng"
            return result

        result = self._fetch_nist(n)
        if result is not None:
            self._last_source = "nist_beacon"
            return result

        result = self._fetch_local(n)
        self._last_source = "os.urandom"
        return result

    def get_seed(self, n_bytes: int = 4) -> int:
        """
        Return an integer seed derived from n_bytes of quantum entropy.

        Args:
            n_bytes: Number of random bytes to use (1–8 typical).

        Returns:
            Non-negative integer suitable for seeding a PRNG.
        """
        raw = self.get_bytes(n_bytes)
        seed = int.from_bytes(raw, "big")
        log = QRNGLog(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            seed=seed,
            source=self._last_source,
            n_bytes=n_bytes,
        )
        try:
            save_qrng_log(log)
        except Exception as exc:
            logger.debug("Could not write QRNG log: %s", exc)
        return seed

    def get_float(self) -> float:
        """
        Return a float in [0.0, 1.0) derived from 4 bytes of quantum entropy.
        """
        raw = self.get_bytes(4)
        value = int.from_bytes(raw, "big")
        return value / (2 ** 32)

    def get_int(self, low: int, high: int) -> int:
        """
        Return a random integer in [low, high) using quantum entropy.

        Args:
            low: Lower bound (inclusive).
            high: Upper bound (exclusive).
        """
        if high <= low:
            raise ValueError(f"high ({high}) must be greater than low ({low})")
        span = high - low
        raw_float = self.get_float()
        return low + int(raw_float * span)

    def get_temperature(self, base: float = 0.1, variance: float = 0.3) -> float:
        """
        Return a temperature float appropriate for LLM inference variance studies.

        Maps quantum entropy to a temperature value centred on `base` with
        maximum deviation of `variance` in each direction.

        Args:
            base: Centre temperature (e.g. 0.1 for near-deterministic).
            variance: Maximum deviation from base (result clamped to [0.0, 2.0]).

        Returns:
            Temperature float in [max(0.0, base-variance), min(2.0, base+variance)].
        """
        offset = (self.get_float() * 2.0 - 1.0) * variance
        temp = base + offset
        return max(0.0, min(2.0, temp))


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

_default_source = QRNGSource()


def get_quantum_seed(n_bytes: int = 4) -> int:
    """Return an integer seed from the default QRNG source."""
    return _default_source.get_seed(n_bytes=n_bytes)


def get_quantum_float() -> float:
    """Return a float in [0.0, 1.0) from the default QRNG source."""
    return _default_source.get_float()


def get_quantum_bytes(n: int = 8) -> bytes:
    """Return n raw bytes from the default QRNG source."""
    return _default_source.get_bytes(n)


def get_quantum_temperature(base: float = 0.1, variance: float = 0.3) -> float:
    """Return an LLM temperature float derived from quantum entropy."""
    return _default_source.get_temperature(base=base, variance=variance)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        description="Fetch quantum random entropy from ANU QRNG / NIST Beacon / os.urandom"
    )
    parser.add_argument("--bytes", type=int, default=4, metavar="N",
                        help="Number of random bytes to fetch (default: 4)")
    parser.add_argument("--seed", action="store_true",
                        help="Print integer seed derived from random bytes")
    parser.add_argument("--float", action="store_true", dest="as_float",
                        help="Print float in [0.0, 1.0)")
    parser.add_argument("--temperature", action="store_true",
                        help="Print LLM temperature float")
    parser.add_argument("--base", type=float, default=0.1,
                        help="Base temperature (default: 0.1)")
    parser.add_argument("--variance", type=float, default=0.3,
                        help="Temperature variance (default: 0.3)")
    args = parser.parse_args()

    src = QRNGSource()

    if args.as_float:
        val = src.get_float()
        print(f"float   : {val:.8f}")
        print(f"source  : {src.source_name}")
    elif args.temperature:
        temp = src.get_temperature(base=args.base, variance=args.variance)
        print(f"temperature : {temp:.4f}")
        print(f"source      : {src.source_name}")
    else:
        n = args.bytes
        if args.seed:
            seed = src.get_seed(n_bytes=n)
            print(f"seed    : {seed}")
        else:
            raw = src.get_bytes(n)
            print(f"bytes   : {raw.hex()}")
        print(f"source  : {src.source_name}")
