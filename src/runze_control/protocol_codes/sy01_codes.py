"""Protocol codes exclusive to SY01B multichannel Syringe Pumps."""
from enum import IntEnum
from itertools import chain
from runze_control.protocol_codes.common_codes import CommonCmd as RunzeCommonCmd


# WARNING: the names of these enums are shared with SyringePumpCommonCmd,
#   but not all values are the same!

class SY01CommonCmd(IntEnum):
    """Codes to issue when querying/specifying the states of various settings
       via a Common Command frame."""
    # Queries
    # Cmds 0x20 - 0x23 come from RunzeCommonCmd
    # Do we not have 0x25, 0x27?
    GetPowerOnResetState = 0x2E
    GetCANDestinationAddress = 0x30
    GetMulticastChannel1Address = 0x70
    GetMulticastChannel2Address = 0x71
    GetMulticastChannel3Address = 0x72
    GetMulticastChannel4Address = 0x73
    GetCurrentChannelAddress = 0xAE
    GetCurrentVersion = 0x3F
    GetMotorStatus = 0x4A
    GetValveStatus = 0x4D  # WARNING: Clashes with movement cmd for single channel syringe pump.
    GetSyringePosition = 0x66  # Get syringe pump position.
    SynchronizeSyringePosition = 0x67  # Zero current position and get position.
                                       # Not sure why this is a query.
    # Commands
    RunInCW = 0x42  # Move valve clockwise a specified number of encoder steps.
    RunInCCW = 0x43  # Move valve counterclockwise a specified number of encoder
                     # steps.
    MoveValveToPort = 0x44  # Move valve to the port specified by B4. The
                            # approach direction is determined automatically.
                            # Values range from 1-N, where N is the number of
                            # ports. Approach direction cannot be specified.
    ResetValvePosition = 0x4C  # Move valve to reset position and stop.
    ResetSyringePosition = 0x45  # Move syringe plunger to the start of travel.
                                 # "Reset and home."
    ForceStop = 0x49  # immediately stop moving the syringe and valve rotor.
    SetDynamicSpeed = 0x4B  # Set plunger speed.
    MovePlungerAbsolute = 0x4E  # Move syringe plunger to an absolute position
                                # in steps [0-6000].
    ForcedReset = 0x4F  # Move syringe plunger to the start of travel and
                        # back off by a small amount (improves service life.)


# FIXME: we should be doing dict-like updates here so that later cmds with
#   the same name overwrite the previous cmd since we are building these
#   containers of codes general-to-specific.
# Combine enums
# https://stackoverflow.com/a/41807919/3312269
CommonCmd = IntEnum('CommonCmd',
                    [(i.name, i.value) for i in chain(RunzeCommonCmd, SY01CommonCmd)])
