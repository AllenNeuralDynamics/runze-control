"""Syringe Pump Driver."""
from serial import Serial, SerialException
from runze_control.device_codes import *
import struct


class SY01B:
    """SY-01B Syringe Pump Serial Driver."""

    DEFAULT_TIMEOUT_S = 1.0  # Default communication timeout in seconds.
    VALID_RS232_AND_RS485_BAUDRATES_BPS = [9600, 19200, 38400, 57600, 115200]

    def __init__(self, port: str, baudrate: int = None):
        self.ser = None
        self.log = logging.getLogger(__name__)
        # if baudrate is unspecified, try all of them before giving up.
        baudrates = [baudrate] if baudrate is not None
                    else SY01B.VALID_RS232_AND_RS485_BAUDRATES_BPS
        # Try all valid baud rates.
        try:
            for br in baudrates:
                try:
                    self.log.debug(f"Connecting to SY-01B on port: " \
                                   f"{com_port} at {br}bps.")
                    self.ser = Serial(com_port, br,
                                      timeout=SY01B.DEFAULT_TIMEOUT_S)
                    break
                except SerialException as e:
                    # Raise exception only if we've tried all valid baud rates.
                    self.log.debug(f"Connecting failed.")
                    if br == baudrates[-1]:
                        raise
        except SerialException as e:
            logging.error("Error: could not open connection to SY-01B. "
                  "Is the device plugged in? Is another program using it?")
            raise
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        # TODO: how do we get or specify the device address?
        self.address = 0x00

    def reset(self):
        pass

    def get_syringe_position(self):
        pass

    def move_valve_clockwise(self, steps):
        pass

    def move_valve_counterclockwise(self, steps):
        pass

    def infuse(self):
        pass

    def draw(self):
        pass

    def select_port(self, port_num):
        pass

    def _send_common_cmd(self, func, b3, b4):
        cmd_bytes = struct.pack(PacketFormat.SendCommon, self.address, func,
                                b3, b4)
        # return reply struct.
        return self._send(cmd_bytes)

    def _send_factory_cmd(self, address, param_value):
        # Pack Factory Cmd PWD Code
        cmd_bytes = struct.pack(PacketFormat.SendFactory, self.address, func,
                                FACTORY_CMD_PWD_CODE, b3, b4)
        return self._send(cmd_bytes)

    def _send(self, cmd: bytes):
        # Construct checksum (bytes 1-6).
        checksum = sum(bytearray(cmd))
        packet = cmd+checksum
        self.log.debug(f"Sending: {repr(str(packet))}"
        self.ser.send(cmd+checksum)
        reply = self.ser.read(REPLY_NUM_BYTES)
        self.log.debug(f"Reply: {repr(reply)}")
        return reply

