"""Syringe pump device codes."""
from enum import IntEnum
from itertools import chain
from runze_control.protocol_codes.syringe_pump_codes import CommonCmd as SyringePumpCommonCmd


class SY08CommonCmd(IntEnum):
    """SY08-exclusive Common command codes to issue when querying/specifying
        the states of various settings via a Common Command frame. Codes
        common to all devices are part of runze_protocol_codes.CommonCmdCode"""
    # Commands
    MoveSyringeAbsolute = 0x4E # [0x0000 - 0x2EE0]
    RunInCCW = 0x4D


# Combine enums
# https://stackoverflow.com/a/41807919/3312269
CommonCmd = IntEnum('CommonCmd',
                    [(i.name, i.value)
                     for i in chain(SyringePumpCommonCmd, SY08CommonCmd)])
