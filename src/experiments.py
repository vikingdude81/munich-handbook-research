from dataclasses import dataclass


@dataclass
class Experiment:
    id: str
    title: str
    spirits_invoked: list[str]
    materials: list[str]
    procedure: str
    source_ref: str
