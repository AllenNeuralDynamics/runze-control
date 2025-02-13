"""Shared syringe pump device codes."""
from enum import IntEnum
from itertools import chain
from runze_control.runze_protocol import CommonCmd as RunzeCommonCmd


class SyringePumpCommonCmd(IntEnum):
    """Runze Protocol codes shared between syringe pumps to issue
       when querying/specifying the states of various settings via a
       Common Command frame. Codes common to all devices are part of
        runze_protocol_codes.CommonCmdCode"""
    # Queries
    GetSubdivision = 0x25   # microstep subdivision?
    GetMaxSpeed = 0x27
    GetCanDestinationAddress = 0x30
    GetCurrentChannelPosition = 0x3E
    GetCurrentFirmwareVersion = 0x3F
    GetMotorStatus = 0x4A # More of an "actuator" status depending on device.
    GetPistonPosition = 0x66
    SynchronizePistonPosition = 0x67
    GetMulticastChannel1Address = 0x70
    GetMulticastChannel2Address = 0x71
    GetMulticastChannel3Address = 0x72
    GetMulticastChannel4Address = 0x73
    # Commands
    RunInCW = 0x42 # Dispense. (i.e: move relative)
    # FIXME: 0x4D is query valve status on SY03 multiport syringe pumps and
    # aspirate on SY08 pumps:
    RunInCCW = 0x4D # Aspirate (i.e: move relative)
    Reset = 0x45
    ForcedReset = 0x4F
    SetDynamicSpeed = 0x4B
    ForceStop = 0x49
    #FIXME: remove shared commands

# Combine enums
# https://stackoverflow.com/a/41807919/3312269

CommonCmd = IntEnum('CommonCmd',
                    [(i.name, i.value) for i in chain(RunzeCommonCmd, SyringePumpCommonCmd)])
