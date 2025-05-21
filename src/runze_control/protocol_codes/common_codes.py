"""Protocol codes common to all devices"""
from enum import Enum, IntEnum


class CommonCmd(IntEnum):
    GetAddress = 0x20
    GetRS232Baudrate = 0x21
    GetRS485Baudrate = 0x22
    GetCanBaudRate = 0x23

    GetCanDestinationAddress = 0x30
    GetFirmwareVersion = 0x3F


class FactoryCmd(IntEnum):
    """Codes for specifying the states of various calibration settings."""
    SetAddress = 0x00
    SetRS232Baudrate = 0x01
    SetRS485Baudrate = 0x02
    SetCANBaudrate = 0x03
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
