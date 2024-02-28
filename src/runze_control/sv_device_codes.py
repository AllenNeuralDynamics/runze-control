"""Syringe pump device codes."""
from enum import IntEnum

# Port-to-Port Dead Volumes for various specific models
# TODO: make dict, keyed by part number sub-fields.
SV01_DEAD_VOLUME_UL = 4.5
SV07_X_S_T6_DEAD_VOLUME_UL = 27.5
SV07_X_S_T8_DEAD_VOLUME_UL = SV07_X_S_T6_DEAD_VOLUME_UL
SV07_X_S_T10_DEAD_VOLUME_UL = SV07_X_S_T6_DEAD_VOLUME_UL
SV07_X_S_T12_DEAD_VOLUME_UL = 22.43
SV07_X_S_T16_DEAD_VOLUME_UL = 33.68


class CommonCmdCode(IntEnum):
    """Codes to issue when querying/specifying the states of various settings
       via a Common Command frame."""
    # Queries
    GetAddress = 0x20
    GetRS232BaudRate = 0x21
    GetRS485BaudRate = 0x22
    GetCANBaudRate = 0x23
    GetPowerOnReset = 0x2E
    GetCANDestinationAddress = 0x30
    GetMulticastCh1Address = 0x70
    GetMulticastCh2Address = 0x71
    GetMulticastCh3Address = 0x72
    GetMulticastCh4Address = 0x73
    GetCurrentChannelAddress = 0x3E
    GetCurrentVersion = 0x3F
    GetMotorStatus = 0x4A
    # Commands
    ValveClockwiseMoveSteps  = 0x42
    ValveCounterClockwiseMoveSteps = 0x43
    ResetSyringePosition = 0x45  # move the syringe to the start of travel.
    Halt = 0x49  # immediately stop moving the syringe and valve rotor.
    SetSpeed = 0x4B  # TODO: plunger or valve stator speed?
    GetSyringePostion = 0x66  # Get syringe pump address(?) TODO and possibly the position too?
    SyncSyringePumpPosition = 0x67  # TODO: what does this actually do?

