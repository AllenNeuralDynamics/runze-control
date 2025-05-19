"""Syringe Pump Driver."""
import logging
from runze_control.protocol import Protocol
from runze_control.syringe_pump import SyringePump
from runze_control.rotary_valve import RotaryValve
from runze_control.protocol_codes import sy01_codes
from typing import Union


# FIXME: consider NOT doing diamond inheritance since Rotary Valve interface
# is totally different!
class MultiChannelSyringePump(RotaryValve, SyringePump):
    """syringe pump with integrated rotary valve."""

    def __init__(self, com_port: str, baudrate: int = None,
                 address: int = 0x31,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 syringe_volume_ul: float = None, position_count: int = None,
                 position_map: dict = None):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
           `syringe_volume_ul` and `port_count` specifications are optional,
           but enables volume and port-centric methods, rather than methods
           that rely on the number of encoder steps.
        """
        print(f"locals in MultichannelSyringePump: {locals()}")
        super().__init__(com_port=com_port, baudrate=baudrate, address=address,
                         protocol=protocol,
                         syringe_volume_ul=syringe_volume_ul,
                         position_count=position_count,
                         position_map=position_map)
        self.codes = sy01_codes  # Overwrite parent class codes.
        # Override logger and logger name.
        logger_name = self.__class__.__name__ + f".{com_port}"
        self.log = logging.getLogger(logger_name)
        # FIXME: validate port count.
        self.position_count = position_count

    # FIXME: we need to suppress some rotary valve functions not available
    #   on the multichannel syringe pump configuration

    def move_valve_to_position(self, position: int, wait: bool = True):
        self._send_common_cmd_runze(self.codes.CommonCmd.MoveValveToPort,
                                    position, wait=wait)




class SY01B(MultiChannelSyringePump):
    """ZSB-SY01B Syringe pump"""
    VALID_PORT_COUNT = [6, 9, 12]
    SYRINGE_MAX_POSITION_STEPS = 6000

    DEFAULT_SPEED_PERCENT = 60.

    SYRINGE_VOLUMES_UL = {25, 50, 125, 500, 1250, 2500, 5000}
    # All volume variants have the same RPM and position.
    SYRINGE_VOLUME_TO_MAX_RPM = {v: 450 for v in SYRINGE_VOLUMES_UL}
    MAX_POSITION_STEPS = {v: 6000 for v in SYRINGE_VOLUMES_UL}

