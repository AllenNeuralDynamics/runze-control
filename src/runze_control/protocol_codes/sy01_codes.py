"""Protocol codes exclusive to SY01B multichannel Syringe Pumps."""
from enum import IntEnum
from itertools import chain
from runze_control.protocol_codes.syringe_pump_codes import CommonCmd as SyringeCommonCmd


# WARNING: the names of these enums are shared with SyringePumpCommonCmd,
#   but not all values are the same!

class SY01CommonCmd(IntEnum):
    """Codes to issue when querying/specifying the states of various settings
       via a Common Command frame."""
    # Queries
    # Cmds 0x20 - 0x23 come from RunzeCommonCmd
    GetPowerOnResetState = 0x2E
    GetCurrentChannelAddress = 0xAE

    GetValveStatus = 0x4D  # WARNING: Clashes with movement cmd for single channel syringe pump.
    # Commands
    RunInCCW = 0x43  # Move valve counterclockwise a specified number of encoder
                     # steps.
    MoveValveToPort = 0x44  # Move valve to the port specified by B4. The
                            # approach direction is determined automatically.
                            # Values range from 1-N, where N is the number of
                            # ports. Approach direction cannot be specified.
    ResetValvePosition = 0x4C  # Move valve to reset position and stop.
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
                    [(i.name, i.value) for i in chain(SyringeCommonCmd, SY01CommonCmd)])
