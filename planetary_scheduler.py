"""
planetary_scheduler.py — Planetary hour scheduler for model/node assignment.

Maps the Munich Handbook's planetary day/hour system to GPU cluster scheduling.
The handbook assigns spirits to planets; we assign models to planetary hours.

Medieval manuscripts (including the Munich Handbook, the Heptameron, and
the Picatrix) treat the planets as governors of specific types of work:
  - Saturn governs binding, constraint, limitation → safety validation
  - Jupiter governs expansion, synthesis, abundance → large-context tasks
  - Mars governs force, war, compulsion → retry/escalation
  - Sun governs illumination, knowledge, authority → primary reasoning
  - Venus governs harmony, love, beauty → embedding/sentiment
  - Mercury governs communication, speed, trickery → fast JSON tasks
  - Moon governs reflection, change, mediation → lightweight relay

The Munich Handbook uses:
  - 7 planets: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
  - Planetary hours cycle through the week starting from the ruling planet of the day
  - Each planet governs specific types of work

Usage:
    from planetary_scheduler import get_current_planetary_hour, get_model_for_now
    from planetary_scheduler import PlanetaryScheduler

    scheduler = PlanetaryScheduler()
    assignment = scheduler.get_assignment()
    print(assignment.planet, assignment.model, assignment.node)
"""

import datetime
import time
import argparse
from dataclasses import dataclass
from typing import Optional, Callable, Any

# ---------------------------------------------------------------------------
# Planetary constants
# ---------------------------------------------------------------------------

# Chaldean order (outermost to innermost in ancient cosmology)
PLANETARY_SEQUENCE = [
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"
]

# Ruling planet for each day of the week (0=Monday … 6=Sunday in Python isoweekday)
# Python weekday(): 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday,
#                   5=Saturday, 6=Sunday
PLANETARY_DAYS = {
    "Monday":    "Moon",
    "Tuesday":   "Mars",
    "Wednesday": "Mercury",
    "Thursday":  "Jupiter",
    "Friday":    "Venus",
    "Saturday":  "Saturn",
    "Sunday":    "Sun",
}

# Precompute the 24-hour planetary sequence for each weekday.
# The first hour of a day is ruled by the day's ruling planet.
# Subsequent hours rotate through the Chaldean sequence.
def _build_planetary_hours() -> dict:
    """Return dict mapping weekday name → list of 24 planet names."""
    hours = {}
    for day, ruler in PLANETARY_DAYS.items():
        start_idx = PLANETARY_SEQUENCE.index(ruler)
        day_hours = []
        for h in range(24):
            planet = PLANETARY_SEQUENCE[(start_idx + h) % 7]
            day_hours.append(planet)
        hours[day] = day_hours
    return hours

PLANETARY_HOURS: dict = _build_planetary_hours()

# ---------------------------------------------------------------------------
# Cluster model assignments
# ---------------------------------------------------------------------------

MODEL_ASSIGNMENTS = {
    "Sun":     "qwen3-coder-next:120b",  # illumination, knowledge retrieval, primary reasoning
    "Moon":    "qwen3:1.7b",             # reflection, boy-medium proxy, lightweight relay
    "Mars":    "qwen3.5:9b",             # force, compulsion, retry/escalation work
    "Mercury": "qwen3.5:9b",             # communication, fast tasks, JSON formatting
    "Jupiter": "qwen3.5:35b",            # expansion, synthesis, large-context tasks
    "Venus":   "qwen3.5:9b",             # harmony, embedding similarity, sentiment
    "Saturn":  "qwen3.5:9b",             # binding, constraint checking, safety validation
}

NODE_ASSIGNMENTS = {
    "Sun":     "brainstorm",     # RTX 5090 — 120B primary
    "Moon":    "3060-worker",    # RTX 3060 — lightweight relay
    "Mars":    "4070-worker",    # RTX 4070 — escalation
    "Mercury": "4070-worker",    # RTX 4070 — fast tasks
    "Jupiter": "brainstorm",     # RTX 5090 — large context
    "Venus":   "a2000-worker",   # A2000 — embedding
    "Saturn":  "a2000-worker",   # A2000 — safety validation
}

# Spirits associated with each planet (from Munich Handbook mappings)
SPIRIT_PLANETARY = {
    "Lucifer":    "Sun",
    "Beelzebub":  "Jupiter",
    "Astaroth":   "Venus",
    "Berith":     "Mars",
    "Asmodeus":   "Mars",
    "Baal":       "Sun",
    "Agares":     "Saturn",
    "Marbas":     "Mercury",
    "Valefor":    "Moon",
    "Barbatos":   "Jupiter",
    "Paimon":     "Moon",
    "Buer":       "Jupiter",
    "Gusion":     "Moon",
    "Sitri":      "Venus",
    "Beleth":     "Moon",
    "Zepar":      "Venus",
    "Samael":     "Mars",
    "Abaddon":    "Saturn",
    "Lilith":     "Moon",
    "Mephistopheles": "Mercury",
}

# Work type → governing planet mapping
WORK_TYPES = {
    "knowledge_retrieval":  "Sun",
    "binding_validation":   "Saturn",
    "escalation_retry":     "Mars",
    "fan_out":              "Jupiter",
    "embedding":            "Venus",
    "safety_check":         "Saturn",
    "session_teardown":     "Moon",
    "fast_json":            "Mercury",
    "synthesis":            "Jupiter",
    "lightweight_relay":    "Moon",
}

# Human-readable description per planet work type
PLANET_WORK_DESC = {
    "Sun":     "illumination, knowledge retrieval, primary reasoning",
    "Moon":    "reflection, lightweight relay, session mediation",
    "Mars":    "force, compulsion, retry/escalation",
    "Mercury": "communication, fast tasks, JSON formatting",
    "Jupiter": "expansion, synthesis, large-context tasks",
    "Venus":   "harmony, embedding similarity, sentiment analysis",
    "Saturn":  "binding, constraint checking, safety validation",
}


# ---------------------------------------------------------------------------
# PlanetaryAssignment dataclass
# ---------------------------------------------------------------------------

@dataclass
class PlanetaryAssignment:
    """Result of a planetary hour scheduling query."""
    planet: str
    model: str
    node: str
    hour_number: int       # 0-23
    day_name: str
    timestamp: str
    ruling_spirit: str     # primary spirit associated with this planet
    work_type: str         # primary work type for this planet


# ---------------------------------------------------------------------------
# PlanetaryScheduler
# ---------------------------------------------------------------------------

class PlanetaryScheduler:
    """
    Maps the current moment in time to a planetary assignment.

    Each query returns the planet ruling the current hour according to
    the Chaldean planetary hour system, along with the associated GPU
    node, model, and ruling spirit from the Munich Handbook.
    """

    def get_current_hour_index(self) -> int:
        """Return the current hour index (0–23) in local time."""
        return datetime.datetime.now().hour

    def get_day_name(self, dt: Optional[datetime.datetime] = None) -> str:
        """Return the day name (e.g. 'Monday') for the given datetime."""
        if dt is None:
            dt = datetime.datetime.now()
        return dt.strftime("%A")

    def get_ruling_planet(self, weekday: str, hour: int) -> str:
        """
        Return the planet ruling the given hour on the given weekday.

        Args:
            weekday: Day name, e.g. 'Monday'.
            hour: Hour index 0–23.

        Returns:
            Planet name string.
        """
        return PLANETARY_HOURS[weekday][hour]

    def get_assignment(self, dt: Optional[datetime.datetime] = None) -> PlanetaryAssignment:
        """
        Return the full planetary assignment for a given datetime.

        Args:
            dt: Datetime to query (default: now).

        Returns:
            PlanetaryAssignment with planet, model, node, and metadata.
        """
        if dt is None:
            dt = datetime.datetime.now()
        day_name = dt.strftime("%A")
        hour = dt.hour
        planet = self.get_ruling_planet(day_name, hour)
        model = MODEL_ASSIGNMENTS[planet]
        node = NODE_ASSIGNMENTS[planet]

        # Find a representative ruling spirit for this planet
        ruling_spirit = next(
            (spirit for spirit, p in SPIRIT_PLANETARY.items() if p == planet),
            planet,
        )

        # Find the primary work type for this planet
        work_type = next(
            (wt for wt, p in WORK_TYPES.items() if p == planet),
            "general",
        )

        return PlanetaryAssignment(
            planet=planet,
            model=model,
            node=node,
            hour_number=hour,
            day_name=day_name,
            timestamp=dt.isoformat(),
            ruling_spirit=ruling_spirit,
            work_type=work_type,
        )

    def get_best_time_for_work(self, work_type: str) -> datetime.datetime:
        """
        Return the next datetime when the appropriate planet rules.

        Args:
            work_type: One of the keys in WORK_TYPES.

        Returns:
            datetime of the next hour governed by the appropriate planet.

        Raises:
            ValueError: If work_type is not recognised.
        """
        if work_type not in WORK_TYPES:
            raise ValueError(
                f"Unknown work_type '{work_type}'. "
                f"Available: {sorted(WORK_TYPES.keys())}"
            )
        target_planet = WORK_TYPES[work_type]
        now = datetime.datetime.now()
        candidate = now.replace(minute=0, second=0, microsecond=0)
        # Search forward up to 7 days (168 hours)
        for _ in range(168):
            day_name = candidate.strftime("%A")
            planet = self.get_ruling_planet(day_name, candidate.hour)
            if planet == target_planet and candidate > now:
                return candidate
            candidate += datetime.timedelta(hours=1)
        # Should never reach here given 168-hour window covers a full week
        raise RuntimeError(f"Could not find next {target_planet} hour within 7 days")

    def schedule_task(
        self,
        task_fn: Callable[[], Any],
        work_type: str,
        force: bool = False,
    ) -> Any:
        """
        Optionally wait for the appropriate planetary hour, then call task_fn.

        Args:
            task_fn: Callable to invoke.
            work_type: Work type key from WORK_TYPES.
            force: If True, call task_fn immediately without waiting.

        Returns:
            Return value of task_fn.
        """
        if force:
            print(f"[planetary] --force: running immediately (work_type={work_type})")
            return task_fn()

        target_planet = WORK_TYPES.get(work_type, None)
        current = self.get_assignment()
        if current.planet == target_planet:
            print(f"[planetary] Current hour is {current.planet} hour — running now.")
            return task_fn()

        next_time = self.get_best_time_for_work(work_type)
        wait_seconds = (next_time - datetime.datetime.now()).total_seconds()
        print(
            f"[planetary] Waiting {wait_seconds/60:.1f} min until "
            f"{target_planet} hour at {next_time.strftime('%H:%M %A')} …"
        )
        time.sleep(wait_seconds)
        return task_fn()

    def print_week_schedule(self) -> None:
        """Print a formatted 7-day × 24-hour planetary hour grid to stdout."""
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        planet_abbr = {
            "Saturn": "SAT", "Jupiter": "JUP", "Mars": "MAR",
            "Sun": "SUN", "Venus": "VEN", "Mercury": "MER", "Moon": "MON",
        }
        print("\n" + "=" * 76)
        print(f"{'PLANETARY HOUR SCHEDULE':^76}")
        print(f"{'(Chaldean system — Munich Handbook mapping)':^76}")
        print("=" * 76)
        header = f"{'Hr':>3}  " + "  ".join(f"{d[:3]:>4}" for d in days)
        print(header)
        print("-" * 76)
        for hour in range(24):
            row = f"{hour:>3}  "
            row += "  ".join(
                f"{planet_abbr[PLANETARY_HOURS[day][hour]]:>4}" for day in days
            )
            print(row)
        print("=" * 76)
        print("\nModel assignments:")
        for planet, model in MODEL_ASSIGNMENTS.items():
            node = NODE_ASSIGNMENTS[planet]
            print(f"  {planet_abbr[planet]} ({planet:8s}) → {model:28s} [{node}]")
        print()


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

_default_scheduler = PlanetaryScheduler()


def get_current_planetary_hour() -> str:
    """Return the planet name ruling the current hour."""
    assignment = _default_scheduler.get_assignment()
    return assignment.planet


def get_model_for_now() -> str:
    """Return the recommended model for the current planetary hour."""
    assignment = _default_scheduler.get_assignment()
    return assignment.model


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Munich Handbook Planetary Hour Scheduler"
    )
    parser.add_argument("--week", action="store_true",
                        help="Print full 7-day × 24-hour planetary schedule")
    parser.add_argument("--next", metavar="WORK_TYPE",
                        help="Show next optimal time for given work type")
    args = parser.parse_args()

    scheduler = PlanetaryScheduler()

    if args.week:
        scheduler.print_week_schedule()
    elif args.next:
        try:
            next_time = scheduler.get_best_time_for_work(args.next)
            planet = WORK_TYPES[args.next]
            model = MODEL_ASSIGNMENTS[planet]
            print(f"Next {args.next} window:")
            print(f"  Planet : {planet}")
            print(f"  Time   : {next_time.strftime('%A %Y-%m-%d %H:%M')}")
            print(f"  Model  : {model}")
            print(f"  Node   : {NODE_ASSIGNMENTS[planet]}")
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Available work types: {sorted(WORK_TYPES.keys())}")
    else:
        assignment = scheduler.get_assignment()
        print("=" * 50)
        print("CURRENT PLANETARY ASSIGNMENT")
        print("=" * 50)
        print(f"  Timestamp      : {assignment.timestamp}")
        print(f"  Day            : {assignment.day_name}")
        print(f"  Hour           : {assignment.hour_number:02d}:xx")
        print(f"  Planet         : {assignment.planet}")
        print(f"  Model          : {assignment.model}")
        print(f"  Node           : {assignment.node}")
        print(f"  Ruling spirit  : {assignment.ruling_spirit}")
        print(f"  Work type      : {assignment.work_type}")
        print(f"  Description    : {PLANET_WORK_DESC[assignment.planet]}")
        print("=" * 50)
