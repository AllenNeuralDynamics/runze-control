"""Syringe Pump Driver."""
from runze_control.common_device_codes import *
from runze_control.runze_device import RunzeDevice
from runze_control import runze_protocol_codes as runze_codes
from runze_control import sy08_device_codes as sy08_codes
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

    def forced_reset(self):
        """Move syringe pump to the start of travel and back off by a small
           amount."""
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query(runze_protocol.CommonCmdCode.ForcedReset)
            return reply['parameter']
        else:
            raise NotImplementedError

    def reset_valve_position(self):
        self.log.debug("Resetting valve position.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query(sy_codes.CommonCmdCode.ResetValvePosition)
            return reply['parameter']
        else:
            raise NotImplementedError

    def reset_syringe_position(self):
        self.log.debug("Resetting syringe position.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query(sy_codes.CommonCmdCode.ResetSyringePosition)
            return reply['parameter']
        else:
            raise NotImplementedError

    def move_valve_clockwise(self, steps):
        raise NotImplementedError

    def move_valve_counterclockwise(self, steps):
        raise NotImplementedError

    def select_port(self, port_num: int, wait: bool = True):
        raise NotImplementedError
        #self._send_query(sy_codes.MotorStatus)


class SY08(RunzeDevice):
    """Syringe Pump."""

    SYRINGE_VOLUME_TO_MAX_RPM = \
    {
        5: 600, # 5mL syringe volume max rpm
        12.5: 600, # 12.5mL syringe volume max rpm
        25: 500 # 25mL syringe volume max rpm
    }
    MAX_POSITION_STEPS = 12000

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
        if syringe_volume_ul not in self.__class__.SYRINGE_VOLUME_TO_MAX_RPM.keys():
            raise ValueError("Syringe volume is invalid and must be one of "
                "the following values: "
                f"{list(self.__class__.SYRINGE_VOLUME_TO_MAX_RPM.keys())}.")
        self.syringe_volume_ul = syringe_volume_ul
        # Connect to port.
        super().__init__(com_port=com_port, baudrate=baudrate,
                         address=address, protocol=protocol)

    def reset_syringe_position(self):
        """Reset and home the syringe."""
        reply = self._send_query(sy_codes.CommonCmdCode.ResetSyringePosition)
        return reply['parameter']

    def get_syringe_position(self):
        """return the syringe position in linear steps."""
        reply = self._send_query(sy_codes.CommonCmdCode.GetSyringePosition)
        return reply['parameter']

    #@syringe_range_check()
    def aspirate(self, microliters: float):
        # Motor step count syringe size.
        steps = 0
        self.log.debug(f"Aspirating {microliters}[uL] (i.e: "
            f"{steps}/{self.__class__.MAX_POSITION_STEPS} steps).")
        pass

    #@syringe_range_check()
    def dispense(self, microliters: float):
        return self.aspirate(microliters)

    def withdraw(self, microliters: float):
        # Motor step count syringe size.
        pass

    #@syringe_range_check()
    def move_absolute_in_steps(self, steps: int):
        pass

    def move_absolute_in_percent(self, percent: float):
        if (percent > 100) or (percent < 0):
            raise ValueError(f"Requested plunger movement ({percent}) "
                             "is out of range [0 - 100].")
        steps = round(percent / 100.0 * self.__class__.MAX_POSITION_STEPS)
        self.log.debug(f"Moving plunger to {percent}% range (i.e: "
            f"{steps}/{self.__class__.MAX_POSITION_STEPS} steps).")
        self._send_common_cmd(sy_codes.CommonCmdCode.MovePlungerAbsolute,
                              steps)
