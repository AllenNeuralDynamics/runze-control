"""Syringe Pump Driver."""
from serial import Serial, SerialException
from runze_control.common_device_codes import *
from runze_control import runze_protocol_codes as runze_protocol
from typing import Union
from functools import reduce
import logging
import struct


class RunzeDevice:
    """Generic Runze Fluid Serial Device."""

    DEFAULT_TIMEOUT_S = 0.5  # Default communication timeout in seconds.
    VALID_SERIAL_BAUDRATES = [9600, 19200, 38400, 57600, 115200]

    def __init__(self, com_port: str, baudrate: int = None, address: int = 0x31,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 port_count: int = None):
        """Init. Connect to a device with the specified address via an
           RS232 or RS485 interface.
        """
        self.address = address
        self.protocol = protocol
        self.ser = None
        self.log = logging.getLogger(f"{__name__}.{com_port}")
        # if baudrate is unspecified, try all of them before giving up.
        baudrates = [baudrate] if baudrate is not None \
                    else RunzeDevice.VALID_SERIAL_BAUDRATES
        # Try all valid baud rates or the one specified.
        try:
            for br in baudrates:
                try:
                    self.log.debug(f"Connecting to device on port: {com_port} "
                                   f"at {br}[bps] on address: '{address}'.")
                    self.ser = Serial(com_port, br,
                                      timeout=RunzeDevice.DEFAULT_TIMEOUT_S)
                    self.ser.reset_input_buffer()
                    self.ser.reset_output_buffer()
                    # Test link by issuing a protocol-dependent dummy command.
                    self.log.debug("Port open. Sending test string.")
                    if self.protocol == Protocol.RUNZE:
                        reply = self.get_address()
                    # TODO: elif self.protocol == Protocol.DT:
                    # Send a test message.
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

    def init(self):
        # Send protocol-specific handshake.
        if self.protocol == Protocol.RUNZE:
            pass
        elif self.protocol == Protocol.DT:
            # /<address>Z<do it now>
            cmd_str = str(DTCommands.InitClockwise) + "R"
            self._send_dt_cmd(DTCommands.InitClockwise, execute=True)


    # FIXME: is this common to all device types?
    def forced_reset(self):
        reply = self._send_query(runze_protocol.CommonCmdCode.ForcedReset)
        return reply['parameter']

    def set_address(self, address: int):
        """Set the device for this bus (only necessary for RS485)."""
        pass

    def get_address(self):
        self.log.debug("Requesting address.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query(runze_protocol.CommonCmdCode.GetAddress)
            return reply['parameter']
        else:
            raise NotImplementedError

    def set_multicast_address(self, multicast_channel: int, address: int):
        """Set the multicast address for this bus (only necessary for RS485).
        Specifying multiple valves with the same multicast address enables
        sending the same commands to groups of valves simultaneously.
        """
        pass

    def get_rs232_baudrate(self):
        reply = self._send_query(runze_protocol.CommonCmdCode.GetRS232Baudrate)
        return RS232BaudrateReply[reply['parameter']]

    def get_rs485_baudrate(self):
        reply = self._send_query(runze_protocol.CommonCmdCode.GetRS485Baudrate)
        return RS485BaudrateReply[reply['parameter']]

    def get_can_baudrate(self):
        raise NotImplementedError


# Consider refactor where these are more per-protocol "make-packet" functions.
    def _send_cmd_dt(self, cmd_str: str, execute: bool = True):
        cmd_str_bytes = cmd_str.encode('ascii')
        cmd_str_bin_encoding = "B"*len(cmd_str_bytes)
        encoding = f"<B{cmd_str_bin_encoding}B"
        cmd_bytes = struct.pack(encoding,
                                DTProtocolPacketFields.FRAME_START,
                                self.address.encode('ascii'),
                                *cmd_str_bytes,
                                DTProtocolPacketFields.FRAME_END)
        execute_cmd = "R" if execute else ""
        packet = "{DTFields.FRAME_START}{cmd_str}{execute_cmd}"
        return self._send(packet, protocol=Protocol.DT)

    def _send_cmd_oem(self, cmd_str: str, execute: bool = True):
        if execute:
            cmd_str += "R"
        cmd_str_bytes = cmd_str.encode('ascii')
        cmd_str_bin_encoding = "B"*len(cmd_str_bytes)
        encoding = f"<B{cmd_str_bin_encoding}B"
        cmd_bytes = struct.pack(encoding,
                                OEMProtocolPacketFields.STX,
                                self.address,
                                OEMProtocolPacketFields.DEFAULT_SEQUENCE_NUMBER
                                *cmd_str_bytes,
                                OEMProtocolPacketFields.ETX)
        checksum = reduce(lambda a, b: a^b, cmd_bytes) # XOR
        packet = cmd_bytes + checksum.to_bytes(1, 'little')
        return self._send(packet)

    # Runze Protocol cmds are made available through:
    # _send_common_cmd, _send_query, _send_factory_cmd

    def _send_common_cmd(self, func: Union[runze_protocol.CommonCmdCode, int],
                         b3: int, b4: int):
        """Send a common command frame to issue a command over Runze Protocol.
           Return a reply frame as a dict."""
        cmd_bytes = struct.pack(runze_protocol.PacketFormat.SendCommon.value,
                                runze_protocol.PacketFields.STX,
                                self.address, func, b3, b4,
                                runze_protocol.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self.parse_runze_reply(self._send(packet))

    # FIXME: func should hint Union type.
    def _send_query(self, func: int, param_value: int = 0x0000):
        """Send a query and return the reply."""
        b3, b4 = param_value.to_bytes(2, 'little')
        return self._send_common_cmd(func, b3, b4)

    def _send_factory_cmd(self, func: Union[runze_protocol.FactoryCmdCode, int],
                          param_value):
        """Send a factory command frame to issue a command over Runze Protocol.
           Return a reply frame as a dict."""
        # Pack Factory Command password in the appropriate location.
        cmd_bytes = struct.pack(runze_protocol.PacketFormat.SendFactory.value,
                                runze_protocol.PacketFields.STX,
                                self.address, func,
                                FACTORY_CMD_PWD_CODE, param_value,
                                runze_protocol.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self.parse_runze_reply(self._send(packet))

    def parse_runze_reply(self, reply: bytes):
        """Parse reply sent over Runze protocol into fields."""
        reply_struct = struct.unpack(runze_protocol.PacketFormat.Reply.value,
                                     reply)
        return dict(zip(CommonReplyFields, reply_struct))

    def _send(self, packet: bytes, protocol: Protocol = Protocol.DT):
        """Send a message over the specified protocol and return the reply."""
        self.log.debug(f"Sending (hex): {packet.hex(' ')}")
        self.ser.write(packet)
        if protocol == Protocol.RUNZE:
            reply = self.ser.read(REPLY_NUM_BYTES)
        elif protocol == Protocol.DT:
            reply = self.ser.read_until(DTFields.REPLY_FRAME_END.encode('ascii'))
        elif protocol == Protocol.OEM:
            # check checksum.
            raise NotImplementedError("Decoding OEM protocol not yet implemented.")
        self.log.debug(f"Reply (hex): {reply.hex(' ')}")
        if len(reply) == 0:
            raise SerialException("No reply received from device.")
        return reply

