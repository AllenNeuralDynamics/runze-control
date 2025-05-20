"""Protocol codes exclusive to SY01B multichannel Syringe Pumps."""
from enum import IntEnum
from itertools import chain
from runze_control.protocol_codes.syringe_pump_codes import CommonCmd as SyringePumpCommonCmd


# WARNING: the names of these enums are shared with SyringePumpCommonCmd,
#   but not all values are the same!

class MiniSY04CommonCmd(IntEnum):
    """Codes to issue when querying/specifying the states of various settings
       via a Common Command frame."""
    # Queries
    # Cmds 0x20 - 0x23 come from RunzeCommonCmd
    # Other commands in SyringePumpCommand
    GetSubdivision = 0x25
    GetMaxSpeed = 0x27
    GetFirmwareSubVersion = 0xEF

    RunInCCW = 0x4D


# FIXME: we should be doing dict-like updates here so that later cmds with
#   the same name overwrite the previous cmd since we are building these
#   containers of codes general-to-specific.
# Combine enums
# https://stackoverflow.com/a/41807919/3312269
CommonCmd = IntEnum('CommonCmd',
                    [(i.name, i.value) for i in chain(SyringePumpCommonCmd, MiniSY04CommonCmd)])
