"""Protocol codes exclusive to SY01B multichannel Syringe Pumps."""
from enum import IntEnum
from itertools import chain
from runze_control.protocol_codes.common_codes import CommonCmd as RunzeCommonCmd


class RotaryValveCommonCmd(IntEnum):
    pass
    # FIXME: add these!

# FIXME: we should be doing dict-like updates here so that later cmds with
#   the same name overwrite the previous cmd since we are building these
#   containers of codes general-to-specific.
# Combine enums
# https://stackoverflow.com/a/41807919/3312269
CommonCmd = IntEnum('CommonCmd',
                    [(i.name, i.value) for i in chain(RunzeCommonCmd, RotaryValveCommonCmd)])
