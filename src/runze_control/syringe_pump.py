"""Syringe Pump Driver."""
from serial import Serial, SerialException
from runze_control import common_device_codes as codes
from runze_control import sy_device_codes as sy_codes
from typing import Union
import logging
import struct


class SY01B:
    """SY-01B Syringe Pump Serial Driver."""

    DEFAULT_TIMEOUT_S = 1.0  # Default communication timeout in seconds.
    VALID_RS232_AND_RS485_BAUDRATES_BPS = [9600, 19200, 38400, 57600, 115200]
    VALID_PORT_COUNT = [6, 9, 12]

    SYRINGE_MIN_POSITION_TICKS = 0x0000
    SYRINGE_MAX_POSITION_TICKS = 0x1770

    def __init__(self, com_port: str, baudrate: int = None,
                 bus_address: int = 0x00, syringe_volume_ul: float = None,
                 port_count: int = None):
        """Init. Connect to a device with the specified address via an
           RS232 interface.
           `syringe_volume_ul` and `port_count` specifications are optional,
           but enables volume and port-centric methods, rather than methods
           that rely on the number of encoder steps.
        """
        self.address = bus_address
        self.syringe_volume_ul = syringe_volume_ul
        # FIXME: if port count is specified, check that it is valid.
        self.port_count = port_count
        self.ser = None
        self.log = logging.getLogger(f"{__name__}.{com_port}")
        # if baudrate is unspecified, try all of them before giving up.
        baudrates = [baudrate] if baudrate is not None \
                    else SY01B.VALID_RS232_AND_RS485_BAUDRATES_BPS
        # Try all valid baud rates or the one specified.
        try:
            for br in baudrates:
                try:
                    self.log.debug(f"Connecting to SY-01B on port: "
                                   f"{com_port} at {br}[bps].")
                    self.ser = Serial(com_port, br,
                                      timeout=SY01B.DEFAULT_TIMEOUT_S)
                    # Test communication by issuing a dummy command.
                    self.log.debug("Port open. Sending test string.")
                    reply = self.get_address()
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

    def set_address(self, address: int):
        """Set the device for this bus (only necessary for RS485)."""
        pass

    def get_address(self):
        reply = self._send_query(sy_codes.CommonCmdCode.GetAddress)
        return reply['parameter']

    def set_multicast_address(self, multicast_channel: int, address: int):
        """Set the multicast address for this bus (only necessary for RS485).
        Specifying multiple valves with the same multicast address enables
        sending the same commands to groups of valves simultaneously.
        """
        pass

    def get_rs232_baud_rate(self):
        reply = self._send_query(sy_codes.CommonCmdCode.GetRS232BaudRate)
        return reply['parameter']

    def get_syringe_position(self):
        """return the syringe position in linear steps."""
        reply = self._send_query(sy_codes.CommonCmdCode.GetSyringePosition)
        return reply['parameter']

    def move_valve_clockwise(self, steps):
        pass

    def move_valve_counterclockwise(self, steps):
        pass

    def dispense_ul(self, microliters: float):
        pass

    def withdraw_ul(self):
        pass

    def select_port(self, port_num: int, wait: bool = True):
        self._send_query(sy_codes.MotorStatus)

    def _send_common_cmd(self, func: Union[sy_codes.CommonCmdCode, int],
                         b3: int, b4: int):
        """Send a common command frame to issue a command.
           Return a reply frame as a dict."""
        cmd_bytes = struct.pack(codes.PacketFormat.SendCommon.value,
                                codes.PacketFields.STX, self.address, func, b3, b4,
                                codes.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self._send(packet)

    # FIXME: func should hint Union type.
    def _send_query(self, func: int, param_value: int = 0x0000):
        """Send a query and return the reply."""
        return self._send_common_cmd(func, 0x00, 0x00)

    def _send_factory_cmd(self, func: Union[codes.FactoryCmdCode, int],
                          param_value):
        # Pack Factory Command password in the appropriate location.
        cmd_bytes = struct.pack(codes.PacketFormat.SendFactory.value,
                                codes.PacketFields.STX, self.address, func,
                                codes.FACTORY_CMD_PWD_CODE, param_value,
                                codes.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self._send(packet)

    def _send(self, packet: bytes):
        self.log.debug(f"Sending (hex): {packet.hex(' ')}")
        self.ser.write(packet)
        reply = self.ser.read(codes.REPLY_NUM_BYTES)
        self.log.debug(f"Reply (hex): {reply.hex(' ')}")
        if len(reply) == 0:
            raise SerialException("No reply received from device.")
        reply_struct = struct.unpack(codes.PacketFormat.Reply.value, reply)
        return dict(zip(codes.CommonReplyFields, reply_struct))

