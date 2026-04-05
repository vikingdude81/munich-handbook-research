from datetime import datetime
import uuid

class SpiritEntity:
    def __init__(self, name, description, legion_count=None):
        self.name = name
        self.description = description
        self.leigon_count = legion_count
        self.provenance = Provenance()

class Provenance:
    def __init__(self):
        self.source = ""
        self.timestamp = datetime.now().isoformat()

def validate_legion_count(legion_count):
    """Validate that legion count is a non-negative integer."""
    if not isinstance(legion_count, int) or legion_count < 0:
        raise ValueError("Legion count must be a non-negative integer.")
    return True

def resolve_rank_alias(rank_name):
    """Resolve alias for rank names (e.g., 'Captain' → 'Rank 1')."""
    # Stub implementation
    if rank_name == "Captain":
        return "Rank 1"
    elif rank_name == "General":
        return "Rank 2"
    else:
        return f"Rank {rank_name}"
