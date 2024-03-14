"""Runze Fluid device codes common across devices."""
from enum import Enum, IntEnum
try:
    from enum import StrEnum  # a 3.11+ feature.
except ImportError:
    class StrEnum(str, Enum):
        pass

class PacketFields(IntEnum):
    """OEM Protocol Packet Fields."""
    STX = 0x02
    ETX = 0x03
    DEFAULT_SEQUENCE_NUMBER = 0x31
