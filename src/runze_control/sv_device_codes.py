"""Syringe pump device codes."""
from enum import Enum


class FactoryCmdCode(Enum):
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


class CommonQueryCode(Enum):
    """Codes to issue when querying the states of various settings."""
    Address = 0x20
    RS232BaudRate = 0x21
    RS485BaudRate = 0x22
    CANBaudRate = 0x23
    PowerOnReset = 0x2E
    CANDestinationAddress = 0x30
    MulticastCh1Address = 0x70
    MulticastCh2Address = 0x71
    MulticastCh3Address = 0x72
    MulticastCh4Address = 0x73
    CurrentChannelAddress = 0x3E
    CurrentVersion = 0x3F
    MotorStatus = 0x4A


class CommonCmdCode(Enum):
    ValveClockwiseMoveSteps  = 0x42
    ValveCounterClockwiseMoveSteps = 0x43
    ResetSyringePosition = 0x45  # move the syringe to the start of travel.
    Halt = 0x49  # immediately stop moving the syringe and valve rotor.
    SetSpeed = 0x4B  # TODO: plunger or valve stator speed?
    GetSyringePostion = 0x66  # Get syringe pump address(?) TODO and possibly the position too?
    SyncSyringePumpPosition = 0x67  # TODO: what does this actually do?

