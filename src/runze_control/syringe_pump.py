"""Syringe Pump Driver."""
from runze_control.common_device_codes import *
from runze_control.runze_device import RunzeDevice
from runze_control import sy_device_codes as sy_codes
from typing import Union


class SY01B(RunzeDevice):
    """Integrated Syringe Pump and Selector Valve."""

    SYRINGE_MIN_POSITION_TICKS = 0x0000
    SYRINGE_MAX_POSITION_TICKS = 0x1770
    VALID_PORT_COUNT = [6, 9, 12]

    def __init__(self, com_port: str, baudrate: int = None,
                 address: int = 0x31,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 syringe_volume_ul: float = None, port_count: int = None):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
           `syringe_volume_ul` and `port_count` specifications are optional,
           but enables volume and port-centric methods, rather than methods
           that rely on the number of encoder steps.
        """
        super().__init__(com_port=com_port, baudrate=baudrate,
                         address=address, protocol=protocol)
        # FIXME: if port count is specified, check that it is valid.
        self.port_count = port_count
        self.syringe_volume_ul = syringe_volume_ul

    def reset_valve_position(self):
        reply = self._send_query(sy_codes.CommonCmdCode.ResetValvePosition)
        return reply['parameter']

    def reset_syringe_position(self):
        self.log.debug("Resetting syringe position.")
        reply = self._send_query(sy_codes.CommonCmdCode.ResetValvePosition)
        return reply['parameter']

    def move_valve_clockwise(self, steps):
        pass

    def move_valve_counterclockwise(self, steps):
        pass

    def select_port(self, port_num: int, wait: bool = True):
        self._send_query(sy_codes.MotorStatus)


class SY08(RunzeDevice):
    """Syringe Pump."""

    def __init__(self, com_port: str, baudrate: int = None,
                 address: int = 0x31,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 syringe_volume_ul: float = None):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
           `syringe_volume_ul` and `port_count` specifications are optional,
           but enables volume and port-centric methods, rather than methods
           that rely on the number of encoder steps.
        """
        super().__init__(com_port=com_port, baudrate=baudrate,
                         address=address, protocol=protocol)
        self.syringe_volume_ul = syringe_volume_ul

    def reset_syringe_position(self):
        """Reset and home the syringe."""
        reply = self._send_query(sy_codes.CommonCmdCode.ResetSyringePosition)
        return reply['parameter']

    def get_syringe_position(self):
        """return the syringe position in linear steps."""
        reply = self._send_query(sy_codes.CommonCmdCode.GetSyringePosition)
        return reply['parameter']

    def dispense(self, microliters: float):
        pass

    def withdraw(self, microliters: float):
        pass
