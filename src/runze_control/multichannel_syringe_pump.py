"""Syringe Pump Driver."""
import logging
from runze_control.protocol import Protocol
from runze_control.syringe_pump import SyringePump
from runze_control.protocol_codes import sy01_codes
from typing import Union


class MultiChannelSyringePump(SyringePump):
    """syringe pump with integrated rotary valve."""

    def __init__(self, com_port: str, baudrate: int = None,
                 address: int = None,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 syringe_volume_ul: float = None, position_count: int = None,
                 position_map: dict = None):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
           `syringe_volume_ul` and `port_count` specifications are optional,
           but enables volume and port-centric methods, rather than methods
           that rely on the number of encoder steps.
        """
        super().__init__(com_port=com_port, baudrate=baudrate, address=address,
                         protocol=protocol,
                         syringe_volume_ul=syringe_volume_ul)
        self.position_count = position_count
        self.position_map = position_map
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



class SY01B(MultiChannelSyringePump):
    """ZSB-SY01B Syringe pump"""
    VALID_PORT_COUNT = [6, 9, 12]
    SYRINGE_MAX_POSITION_STEPS = 6000

    DEFAULT_SPEED_PERCENT = 60.

    SYRINGE_VOLUMES_UL = {25, 50, 125, 500, 1250, 2500, 5000}
    # All volume variants have the same RPM and position.
    SYRINGE_VOLUME_TO_MAX_RPM = {v: 450 for v in SYRINGE_VOLUMES_UL}
    MAX_POSITION_STEPS = {v: 6000 for v in SYRINGE_VOLUMES_UL}

