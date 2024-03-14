"""Runze Fluid device codes common across devices."""
from enum import Enum, IntEnum
try:
    from enum import StrEnum  # a 3.11+ feature.
except ImportError:
    class StrEnum(str, Enum):
        pass

class Protocol(StrEnum):
    RUNZE = "RUNZE"
    OEM = "OEM"
    DT = "DT" # ASCII
