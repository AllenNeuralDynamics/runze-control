"""Runze Fluid device codes common across devices."""
from enum import Enum, IntEnum
try:
    from enum import StrEnum  # a 3.11+ feature.
except ImportError:
    class StrEnum(str, Enum):
        pass


# Create a custom enum that can also be interpreted as a bytes type.
class BytesEnum(bytes, Enum):
    pass


class Protocol(StrEnum):
    RUNZE = "RUNZE"
    OEM = "OEM"
    DT = "DT"  # aka: ASCII


REQUEST_PROTOCOL_MODE = b'\x91\xeb\x07\x00\x00\x00\x00\x00\x00\xd5(\xff\xf8'


class ProtocolReply(BytesEnum):
    """Code issued from the device to indicate whether the device is in
    Runze or Ascii mode."""
    RUNZE = b'\x91\xeb\x02\x01\x00\x63\xd7\xf6\xab\x00'
    DT = b'\x91\xeb\x0a\x01\x00\x02\xc4\x47\x0b\x00'


class SetProtocol(BytesEnum):
    """Codes to change the device to Runze or Ascii mode.
    Sending this codes requires following up by power-cycling the device."""
    RUNZE = b'\x91\xeb\x03\x00\x00\x02\x08\x00\x00\x0c\x0a\x69\x69'
    DT = b'\x91\xeb\x03\x00\x00\x0a\x08\x00\x00\x6d\x19\xd8\xc9'

