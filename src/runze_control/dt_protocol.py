"""Runze Fluid device codes common across devices."""
from enum import Enum, IntEnum
try:
    from enum import StrEnum  # a 3.11+ feature.
except ImportError:
    class StrEnum(str, Enum):
        pass


class PacketFields(StrEnum):
    """DT (i.e: ASCII) Protocol Packet Fields."""
    FRAME_START = '/'  # 0x2F
    FRAME_END = '\r'  # 0x0D
    REPLY_FRAME_END = '\r\n'


class Commands(StrEnum):
    AbsolutePosition = "A"  # Move absolute
    RelativePickup = "P"    # Move relative in the withdraw direction.
    RelativeDispense = "D"  # Move relative in the dispense direction.
    InitClockwise = "Z"
