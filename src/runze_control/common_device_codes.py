"""Runze Fluid device codes common across devices."""
from enum import Enum, IntEnum

FACTORY_CMD_PWD_CODE = 0xFFEEBBAA  # Password for applying factory commands.

REPLY_END_OF_FRAME = 0xDD
REPLY_NUM_BYTES = 8

class PacketFormat(Enum):
    SendCommon = "<BBBBBB" # little-endian, 6 uint8 (checksum omitted)
    SendFactory = "<BBBBBBBBBBBB" # little-endian, 12 uint8 (checksum omitted)

    Reply = "<BBHBBH" # little-endian, 2 uint8, 1 uint16 2 uint8, 1 uint16 (checksum)


class PacketFields(IntEnum):
    STX = 0xCC
    ETX = 0xDD


CommonReplyFields = ('stx', 'addr', 'status', 'parameter', 'etx', 'checksum')


class FactoryCmdCode(IntEnum):
    """Codes for specifying the states of various calibration settings."""
    Address = 0x00
    RS232Baudrate = 0x01
    RS485Baudrate = 0x02
    CANBaudrate = 0x03
    PowerOnReset = 0x0E  # If set (B7=1), the valve will reset to an
                         # interstitial position between port 1 and port N upon
                         # power-up.
    CANDestinationAddress = 0x10
    MulticastCh1Address = 0x50
    MulticastCh2Address = 0x51
    MulticastCh3Address = 0x52
    MulticastCh4Address = 0x53
    ParameterLock = 0xFC
    FactoryReset = 0xFF


class ReplyStatus(IntEnum):
    """Reply codes for the STATUS (B2) field of a reply to a common command."""
    NormalState = 0x00
    FrameError = 0x01
    ParameterError = 0x02
    OptocouplerError = 0x03
    MotorBusy = 0x04
    MotorStalling = 0x05
    UnknownLocations = 0x06
    CommandRejected = 0x07
    IllegalLocation = 0x08
    TaskExecution = 0xFE
    UnknownError = 0xFF
