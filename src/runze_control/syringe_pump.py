"""Syringe Pump Driver."""
from runze_control.protocol import Protocol
from runze_control.runze_protocol  import ReplyStatus
from runze_control.runze_device import RunzeDevice
from runze_control import runze_protocol as runze_codes
from runze_control.protocol_codes import syringe_pump_codes
from runze_control.protocol_codes import sy08_codes
from runze_control.protocol_codes import sy01_codes
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
        self.port_count = port_count
        self.syringe_volume_ul = syringe_volume_ul

    def forced_reset(self):
        """Move syringe pump to the start of travel and back off by a small
           amount."""
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query_runze(sy01_codes.CommonCmd.ForcedReset)
            return reply['parameter']
        else:
            raise NotImplementedError

    def reset_valve_position(self):
        self.log.debug("Resetting valve position.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query_runze(sy01_codes.CommonCmd.ResetValvePosition)
            return reply['parameter']
        else:
            raise NotImplementedError

    def reset_syringe_position(self):
        self.log.debug("Resetting syringe position.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query_runze(sy01_codes.CommonCmd.ResetSyringePosition)
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


class SyringePump(RunzeDevice):

    VALVE_ENCODER_MAX_STEPS = 2048
    SYRINGE_ENCODER_MAX_STEPS = 6000
    MOTOR_MAX_SPEED = 1000

    def __init__(self, com_port: str, baudrate: int = None,
                 address: int = 0x31,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 syringe_volume_ul: int = None):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
           `syringe_volume_ul` is optional
           but enables volume and port-centric methods, rather than methods
           that rely on the number of encoder steps.
        """
        if (syringe_volume_ul is not None
            and syringe_volume_ul not in self.__class__.SYRINGE_VOLUME_TO_MAX_RPM.keys()):
            raise ValueError(f"Syringe volume ({syringe_volume_ul} [uL])is invalid "
                "and must be one of the following values: "
                f"{list(self.__class__.SYRINGE_VOLUME_TO_MAX_RPM.keys())}.")
        self.max_speed_rpm = self.__class__.SYRINGE_VOLUME_TO_MAX_RPM[syringe_volume_ul]
        self.max_position_steps = self.__class__.MAX_POSITION_STEPS[syringe_volume_ul]
        self.syringe_volume_ul = syringe_volume_ul
        self.syringe_speed_percent = None
        self.driver_steps = 0
        # Connect to port.
        super().__init__(com_port=com_port, baudrate=baudrate,
                         address=address, protocol=protocol)

    def reset_syringe_position(self, wait: bool = True):
        """Reset and home the syringe."""
        self.log.debug("Requesting default speed. If device is freshly "
            "powered on, the speed change will not take place until after the "
            "first reset.")
        self.set_speed_percent(self.__class__.DEFAULT_SPEED_PERCENT)
        self.log.debug(f"Resetting syringe (moving to ~0 position).")
        self._send_query_runze(syringe_pump_codes.CommonCmd.Reset)
        # Per datasheet, after reset, the syringe needs to be told that the
        # reset position is the 0 position.
        self.log.debug(f"Synchronizing syringe position.")
        self._send_query_runze(syringe_pump_codes.CommonCmd.SynchronizePistonPosition)
        self.driver_steps = 0  # Reset local step count.
        self.log.debug(f"Syringe reset.")

    def get_position_steps(self):
        """return the syringe position in linear steps."""
        reply = self._send_query_runze(syringe_pump_codes.CommonCmd.GetPistonPosition)
        self.driver_steps = reply["parameter"]  # Update local step count.
        range_percent = self.driver_steps / self.max_position_steps * 100.0
        self.log.debug(f"Syringe position: {self.driver_steps}/"
                       f"{self.max_position_steps} [steps] "
                       f"i.e: {range_percent:.2f}% full-scale range.")
        return self.driver_steps

    def get_position_ul(self):
        return (self.get_position_steps() * self.syringe_volume_ul
                / self.max_position_steps)

    def get_position_percent(self):
        return self.get_position_steps() * 100.0 / self.max_position_steps

    def aspirate(self, microliters: float, wait: bool = True):
        """Relative plunger move to withdraw the specified number of microliters."""
        steps_per_ul = self.max_position_steps / self.syringe_volume_ul
        steps = round(microliters * steps_per_ul)
        self.aspirate_steps(steps, wait=wait)

    def withdraw(self, microliters: float, wait: bool = True):
        """Relative plunger move to withdraw the specified number of microliters."""
        return self.aspirate(microliters, wait)

    def dispense(self, microliters: float, wait: bool = True):
        """Relative plunger move to dispense the specified number of microliters."""
        steps_per_ul = self.max_position_steps / self.syringe_volume_ul
        steps = round(microliters * steps_per_ul)
        self.dispense_steps(steps, wait=wait)

    def aspirate_steps(self, steps: int, wait: bool = True):
        ul = steps * self.syringe_volume_ul / self.max_position_steps
        self.log.debug(f"Aspirating {ul:.2f} [uL] i.e {steps} [steps].")
        self._send_common_cmd_runze(syringe_pump_codes.CommonCmd.RunInCCW, steps, wait)
        self.driver_steps += steps

    def withdraw_steps(self, steps: int, wait: bool = True):
        return self.aspirate_steps(steps, wait=wait)

    def dispense_steps(self, steps: int, wait: bool = True):
        ul = steps * self.syringe_volume_ul / self.max_position_steps
        self.log.debug(f"Dispensing {ul:.2f} [uL] i.e {steps} [steps].")
        self._send_common_cmd_runze(syringe_pump_codes.CommonCmd.RunInCW, steps, wait)
        self.driver_steps -= steps

    def force_stop(self):
        """Halt the syringe pump in its current location."""
        # Always send--even if prior cmd has not been received.
        self._send_common_cmd_runze(syringe_pump_codes.CommonCmd.ForceStop,
                                    wait=True, force=True)
        # Update local step count.
        self.get_position_steps()

    def halt(self):
        return self.force_stop()

    def get_motor_status(self):
        reply = self._send_common_cmd_runze(syringe_pump_codes.CommonCmd.GetMotorStatus)
        return reply['parameter']

    def is_busy(self):
        # Check if we are waiting on replies.
        if super().is_busy():
            return True
        # Check motor status directly. Check for MOTOR_BUSY
        motor_status = self.get_motor_status()
        if motor_status == ReplyStatus.MotorBusy:
            return True
        return False

    def set_speed_percent(self, percent: float, wait: bool = True):
        """Set speed in percent."""
        self.log.debug(f"Setting speed to {percent}%.")
        if (percent > 100) or (percent < 0):
            raise ValueError(f"Requested plunger speed ({percent}%) is out of "
                             f"range [0 - 100].")
        rpm_per_percent = self.max_speed_rpm / 100.0
        speed_rpm = round(percent * rpm_per_percent)
        self.log.debug(f"Setting motor speed to {percent}% "
                       f"(i.e: {speed_rpm}[rpm]).")
        self._send_common_cmd_runze(syringe_pump_codes.CommonCmd.SetDynamicSpeed,
                                    speed_rpm, wait)
        self.syringe_speed_percent = percent # If no errors, save for getter fn.

    def get_speed_percent(self):
        """Return the current speed in percent.
            Note: this value is local and not read directly from the device."""
        return self.syringe_speed_percent

    def get_remaining_capacity_ul(self):
        """return the remaining syringe capacity."""
        raise NotImplementedError

    def move_absolute_in_steps(self, steps: int, wait: bool = True):
        raise NotImplementedError

    def move_absolute_in_percent(self, percent: float, wait: bool = True):
        raise NotImplementedError


class MiniSY04(SyringePump):
    """Mini SY04 Syringe Pump"""

    DEFAULT_SPEED_PERCENT = 60
    SYRINGE_VOLUME_TO_MAX_RPM = \
    {
        5000: 300, # 5mL syringe volume max rpm
        10000: 300, # 10mL syringe volume max rpm
        20000: 250 # 25mL syringe volume max rpm
    }

    # Full Stroke depends on model.
    MAX_POSITION_STEPS = \
    {

        5000: 12000,
        10000: 9632,
        20000: 9600
    }

    def __init__(self, com_port: str, baudrate: int = None,
                 address: int = 0x31, syringe_volume_ul: int = None):
        # Only RUNZE Protocol is supported for MiniSY04.
        super().__init__(com_port=com_port, baudrate=baudrate,
                         address=address, protocol=Protocol.RUNZE,
                         syringe_volume_ul=syringe_volume_ul)

    def move_absolute_in_steps(self, steps: int, wait: bool = True):
        """Absolute move (in steps).

        .. Note::
           This feature is implemented in the software driver rather than
           leveraging a feature on the device itself like the SY08.

        """
        if (steps > self.max_position_steps) or (steps < 0):
            raise ValueError(f"Requested plunger movement ({steps}) is out of "
                             f"range [0 - self.max_position_steps].")
        # No "move-absolute" command exists for this device, so we need to
        # compute a relative move from accumulated steps tracked in the driver.
        desired_steps = steps
        delta_steps = desired_steps - self.driver_steps
        # Sending a 0-step command results in a ParameterError on the device.
        if delta_steps == 0:
            self.log.debug("Not sending a 0-step movement command to device.")
            return
        range_percent = steps/self.max_position_steps * 100.0
        self.log.debug(f"Absolute move to {steps}/"
                       f"{self.max_position_steps} [steps] "
                       f"i.e: {range_percent:.2f}% full-scale range.")
        if delta_steps > 0:
            self.withdraw_steps(delta_steps, wait=wait)
        else:
            self.dispense_steps(abs(delta_steps), wait=wait)

    def move_absolute_in_percent(self, percent: float, wait: bool = True):
        """Absolute move (in percent)."""
        if (percent > 100) or (percent < 0):
            raise ValueError(f"Requested plunger movement ({percent}) "
                             "is out of range [0 - 100].")
        steps = round(percent / 100.0 * self.max_position_steps)
        self.move_absolute_in_steps(steps, wait=wait)


class SY08(SyringePump):
    """SY08 Syringe Pump."""

    DEFAULT_SPEED_PERCENT = 60 # Power-on-reset startup speed.
    SYRINGE_VOLUME_TO_MAX_RPM = \
    {
        5000: 600, # 5mL syringe volume max rpm
        12500: 600, # 12.5mL syringe volume max rpm
        25000: 500 # 25mL syringe volume max rpm
    }

    # Full stroke is the same regardless of syringe model.
    MAX_POSITION_STEPS = \
    {
        5000: 12000,
        12500: 12000,
        25000: 12000
    }

    def force_stop(self):
        """Halt the syringe pump in its current location."""
        # SY08 leaves a residual reply that needs to be cleared if we are
        # halting an active movement command.
        was_busy = super().is_busy()  # Save whether we are waiting on a reply.
        self._send_common_cmd_runze(syringe_pump_codes.CommonCmd.ForceStop,
                                    wait=True, force=True)
        # Clear the irrelevant reply from the aborted command.
        if was_busy:
            self.wait_for_reply(force=True)
        # Update local step count.
        self.get_position_steps()

    def move_absolute_in_steps(self, steps: int, wait: bool = True):
        """Absolute move (in steps)."""
        if (steps > self.max_position_steps) or (steps < 0):
            raise ValueError(f"Requested plunger movement ({steps}) is out of "
                             f"range [0 - self.max_position_steps].")
        range_percent = steps/self.max_position_steps * 100.0
        self.log.debug(f"Absolute move to {steps}/"
                       f"{self.max_position_steps} [steps] "
                       f"i.e: {range_percent:.2f}% full-scale range.")
        self._send_common_cmd_runze(sy08_codes.CommonCmd.MoveSyringeAbsolute,
                                    steps, wait)
        self.driver_steps = steps

    def move_absolute_in_percent(self, percent: float, wait: bool = True):
        """Absolute move (in percent)."""
        if (percent > 100) or (percent < 0):
            raise ValueError(f"Requested plunger movement ({percent}) "
                             "is out of range [0 - 100].")
        steps = round(percent / 100.0 * self.max_position_steps)
        self.log.debug(f"Absolute move to {steps}/"
                       f"{self.max_position_steps} [steps] "
                       f"i.e: {percent:.2f}% full-scale range.")
        self._send_common_cmd_runze(sy08_codes.CommonCmd.MoveSyringeAbsolute,
                                    steps, wait)
        self.driver_steps = steps
