"""Syringe pump device codes."""
from enum import IntEnum


class CommonCmdCode(IntEnum):
    """Codes to issue when querying/specifying the states of various settings
       via a Common Command frame. Codes common to all devices are part of
        runze_protocol_codes.CommonCmdCode"""
    # Queries
    GetSubdivision = 0x25   # microstep subdivision?
    GetMaxSpeed = 0x27
    GetCanDestinationAddress = 0x30
    GetCurrentChannelPosition = 0x3E
    GetCurrentFirmwareVersion = 0x3F
    GetMotorStatus = 0x4A
    GetPistonPosition = 0x66
    SynchronizePistonPosition = 0x67
    GetMulticastChannel1Address = 0x70
    GetMulticastChannel2Address = 0x71
    GetMulticastChannel3Address = 0x72
    GetMulticastChannel4Address = 0x73
    # Commands
    RunInCW = 0x42 # Dispense. (i.e: move relative)
    RunInCCW = 0x4D # Aspirate (i.e: move relative)
    Reset = 0x45
    ForcedReset = 0x4F
    SetDynamicSpeed = 0x4B
    MoveSyringeAbsolute = 0x4E # [0x0000 - 0x2EE0]
    ForceStop = 0x49
