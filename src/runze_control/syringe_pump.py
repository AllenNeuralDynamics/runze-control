"""Syringe Pump Driver."""
from serial import Serial, SerialException
from runze_control.device_codes import *
from runze_control import common_device_codes as common_codes
import struct


class SY01B:
    """SY-01B Syringe Pump Serial Driver."""

    DEFAULT_TIMEOUT_S = 1.0  # Default communication timeout in seconds.
    VALID_RS232_AND_RS485_BAUDRATES_BPS = [9600, 19200, 38400, 57600, 115200]

    def __init__(self, port: str, baudrate: int = None,
                 bus_address: int = 0x00):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
        """
        self.address = bus_address
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

    def reset(self):
        pass

    def set_multicast_address(self, multicast_channel: int, address: int):
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

    def select_port(self, port_num, wait: bool = True):
        if wait:
            self._send_query(MotorStatus.value)
        pass

    def _send_common_cmd(self, func, b3, b4):
        """Send a common command frame to issue a command.
           Return a reply frame as a dict."""
        cmd_bytes = struct.pack(PacketFormat.SendCommon, self.address, func,
                                b3, b4)
        checksum = sum(bytearray(cmd))
        packet = cmd_bytes + checksum
        return self._send(packet)

    def _send_query(self, func: int, param_value: int = 0x0000):
        """Send a common command frame to issue a query.
           Return a reply frame as a dict."""
        cmd_bytes = struct.pack(PacketFormat.SendCommon, self.address, func,
                                param_value)
        checksum = sum(bytearray(cmd))
        packet = cmd_bytes + checksum
        return self._send(packet)

    def _send_factory_cmd(self, func: int, param_value):
        # Pack Factory Command password in the appropriate location.
        cmd_bytes = struct.pack(PacketFormat.SendFactory, self.address, func,
                                FACTORY_CMD_PWD_CODE, b3, b4)
        checksum = sum(bytearray(cmd))
        packet = cmd_bytes + checksum
        return self._send(packet)

    def _send(self, cmd: bytes):
        self.log.debug(f"Sending: {repr(str(packet))}"
        reply = self.ser.read(REPLY_NUM_BYTES)
        self.log.debug(f"Reply: {repr(reply)}")
        reply_struct = struct.unpack(PacketFormat.Reply, reply)
        return dict(zip(reply_fields, common_device_codes.ReplyFields))

