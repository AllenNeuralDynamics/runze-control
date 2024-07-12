"""Syringe Pump Driver."""
from runze_control.common_device_codes import *
from runze_control.runze_protocol_codes  import ReplyStatus
from runze_control.runze_device import RunzeDevice
from runze_control import runze_protocol_codes as runze_codes
from runze_control import sy08_device_codes as sy08_codes
from runze_control import sy01_device_codes as sy01_codes
from typing import Union


class SY01B(RunzeDevice):
    """Multi-Channel Syringe Pump."""

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
            reply = self._send_query(sy01_codes.CommonCmdCode.ResetValvePosition)
            return reply['parameter']
        else:
            raise NotImplementedError

    def reset_syringe_position(self):
        self.log.debug("Resetting syringe position.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query(sy01_codes.CommonCmdCode.ResetSyringePosition)
            return reply['parameter']
        else:
            raise NotImplementedError

    def move_valve_clockwise(self, steps):
        raise NotImplementedError

    def move_valve_counterclockwise(self, steps):
        raise NotImplementedError

    def select_port(self, port_num: int):
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
    MAX_POSITION_STEPS = 12000 # Full stroke is the same regardless of syringe
                               # model.

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

    def reset_syringe_position(self, wait: bool = True):
        """Reset and home the syringe."""
        self.log.debug(f"Resetting syringe to 0[uL] position.")
        reply = self._send_query(sy08_codes.CommonCmdCode.Reset)
        return reply['parameter']

    def get_position(self):
        """return the syringe position in linear steps."""
        reply = self._send_query(sy08_codes.CommonCmdCode.GetPistonPosition)
        return reply['parameter']

    # TODO: in theory, we could track how many times we could aspirate based on
    #   current position.
    def aspirate(self, microliters: float, wait: bool = True):
        steps_per_ul = self.__class__.MAX_POSITION_STEPS / self.syringe_volume_ul
        steps = round(microliters * steps_per_ul)
        self.log.debug(f"Aspirating {microliters}[uL] (i.e: {steps} [steps]).")
        self._send_common_cmd(sy08_codes.CommonCmdCode.RunInCCW, steps, wait)

    def withdraw(self, microliters: float, wait: bool = True):
        return self.aspirate(microliters, wait)

    def dispense(self, microliters: float, wait: bool = True):
        steps_per_ul = self.__class__.MAX_POSITION_STEPS / self.syringe_volume_ul
        steps = round(microliters * steps_per_ul)
        self.log.debug(f"Dispensing {microliters}[uL] (i.e: {steps} [steps]).")
        self._send_common_cmd(sy08_codes.CommonCmdCode.RunInCW, steps, wait)

    def force_stop(self):
        """Halt the syringe pump in its current location."""
        # Always send--even if prior cmd has not been received.
        was_busy = super().is_busy() # Save whether we are waiting on a reply.
        self._send_common_cmd(sy08_codes.CommonCmdCode.ForceStop, wait=True,
                              force=True)
        # Clear the irrelevant reply from the aborted command.
        if was_busy:
            self.wait_for_reply(force=True)

    def halt(self):
        return self.force_stop()

    def get_motor_status(self):
        return self._send_common_cmd(sy08_codes.CommonCmdCode.GetMotorStatus)

    def is_busy(self):
        # Check if we are waiting on replies.
        if super().is_busy():
            return True
        # Check motor status directly. Check for MOTOR_BUSY
        motor_status = self.get_motor_status()
        if motor_status == ReplyStatus.MotorBusy:
            return True
        return False

    def get_remaining_capacity_ul(self):
        """return the remaining syringe capacity."""
        raise NotImplementedError

    def move_absolute_in_steps(self, steps: int, wait: bool = True):
        if (steps > self.__class__.MAX_POSITION_STEPS) or (steps < 0):
            raise ValueError(f"Requested plunger movement ({steps}) is out of "
                             f"range [0 - self.__class__.MAX_POSITION_STEPS].")
        self.log.debug(f"Absolute move to {steps}/"
                       f"{self.__class__.MAX_POSITION_STEPS} [steps].")
        self._send_common_cmd(sy08_codes.CommonCmdCode.MoveSyringeAbsolute,
                              steps, wait)

    def move_absolute_in_percent(self, percent: float, wait: bool = True):
        if (percent > 100) or (percent < 0):
            raise ValueError(f"Requested plunger movement ({percent}) "
                             "is out of range [0 - 100].")
        steps = round(percent / 100.0 * self.__class__.MAX_POSITION_STEPS)
        self.log.debug(f"Absolute move to {percent}% of full scale range "
            f"(i.e: {steps}/{self.__class__.MAX_POSITION_STEPS} [steps]).")
        self._send_common_cmd(sy08_codes.CommonCmdCode.MoveSyringeAbsolute,
                              steps, wait)
