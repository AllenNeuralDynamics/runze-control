"""Runze Fluid device codes common across devices."""
from enum import Enum, IntEnum

try:
    from enum import StrEnum  # a 3.11+ feature.
except ImportError:
    class StrEnum(str, Enum):
        pass

FACTORY_CMD_PWD_CODE = 0xFFEEBBAA  # Password for applying factory commands.
REPLY_NUM_BYTES = 8


class PacketFormat(StrEnum):
    SendCommon = "<BBBBBB" # little-endian, 6 uint8 (checksum omitted)
    SendFactory = "<BBBBBBBBBBBB" # little-endian, 12 uint8 (checksum omitted)
    Reply = "<BBBHBH" # little-endian, 2 uint8, 1 uint16 2 uint8, 1 uint16 (checksum)


class PacketFields(IntEnum):
    """Runze Protocol Packet Fields."""
    STX = 0xCC
    ETX = 0xDD


# Runze Protocol Fields
CommonReplyFields = ('stx', 'addr', 'status', 'parameter', 'etx', 'checksum')


class ReplyStatus(IntEnum):
    """Reply codes for the STATUS (B2) field of a reply to a common command."""
    NormalState = 0x00
    FrameError = 0x01
    ParameterError = 0x02
    OptocouplerError = 0x03
    MotorBusy = 0x04
    MotorStalled = 0x05
    UnknownLocations = 0x06
    CommandRejected = 0x07
    IllegalLocation = 0x08
    TaskExecution = 0xFE
    UnknownError = 0xFF


# Reply codes for RS232Baudrate and RS485Baudrate FactoryCmdCodes.
RS232BaudrateReply = \
{
    0: 9600,
    1: 19200,
    2: 38400,
    3: 57600,
    4: 115200
}

RS485BaudrateReply = RS232BaudrateReply
