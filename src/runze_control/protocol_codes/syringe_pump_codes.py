"""Shared syringe pump device codes."""
from enum import IntEnum
from itertools import chain
from runze_control.protocol_codes.common_codes import CommonCmd as RunzeCommonCmd


class SyringePumpCommonCmd(IntEnum):
    """Runze Protocol codes shared between syringe pumps to issue
       when querying/specifying the states of various settings via a
       Common Command frame. Codes common to all devices are part of
        runze_protocol_codes.CommonCmdCode

    .. WARNING::
       These codes are *not* shared with *multichannel* syringe pumps, which
       use different codes for some of the same commands.

    """
    # Queries
    #GetCurrentChannelPosition = 0x3E
    GetMotorStatus = 0x4A  # More of an "actuator" status depending on device.
    GetSyringePosition = 0x66 # TODO: validate that this works on SY01B
    SynchronizeSyringePosition = 0x67  # This is a query?

    GetMulticastChannel1Address = 0x70
    GetMulticastChannel2Address = 0x71
    GetMulticastChannel3Address = 0x72
    GetMulticastChannel4Address = 0x73
    # Commands
    RunInCW = 0x42  # Dispense. (i.e: move relative)
    # RunInCCW --> depends on model.
    ResetSyringePosition = 0x45  # Move syringe to the start of travel.
    ForceStop = 0x49
    SetDynamicSpeed = 0x4B  # Set syringe speed.


# Combine enums
# https://stackoverflow.com/a/41807919/3312269
CommonCmd = IntEnum('CommonCmd',
                    [(i.name, i.value)
                     for i in chain(RunzeCommonCmd, SyringePumpCommonCmd)])
