"""Syringe Pump Driver."""
from serial import Serial, SerialException
from runze_control.common_device_codes import *
from runze_control import runze_protocol_codes as runze_codes
from runze_control import dt_protocol_codes as dt_codes
from typing import Union
from functools import reduce, wraps
from time import perf_counter
import logging
import struct


class RunzeDevice:
    """Generic Runze Fluid Serial Device."""

    DEFAULT_TIMEOUT_S = 0.25  # Default communication timeout in seconds.
    LONG_TIMEOUT_S = 30.0  # Default communication timeout in seconds.
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
                    elif self.protocol == Protocol.DT:
                        raise NotImplementedError
                    elif self.protocol == Protocol.OEM:
                        raise NotImplementedError
                    break
                except SerialException as e:
                    # Raise exception only if we've tried all valid baud rates.
                    self.log.debug(f"Connecting failed.")
                    if br == baudrates[-1]:
                        raise
        except SerialException as e:
            logging.error("Error: could not open connection to device. "
                "Is it plugged in and powered up? Is another program using it?")
            raise

    def init(self):
        # Send protocol-specific handshake.
        if self.protocol == Protocol.RUNZE:
            pass
        elif self.protocol == Protocol.DT:
            # /<address>Z<do it now>
            cmd_str = str(dt_codes.Commands.InitClockwise) + "R"
            self._send_dt_cmd(dt_codes.Commands.InitClockwise, execute=True)

    def set_address(self, address: int):
        """Set the device for this bus (only necessary for RS485)."""
        pass

    def get_address(self):
        self.log.debug("Requesting address.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query(runze_codes.CommonCmdCode.GetAddress)
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
        reply = self._send_query(runze_codes.CommonCmdCode.GetRS232Baudrate)
        return runze_codes.RS232BaudrateReply[reply['parameter']]

    def get_rs485_baudrate(self):
        reply = self._send_query(runze_codes.CommonCmdCode.GetRS485Baudrate)
        return runze_codes.RS485BaudrateReply[reply['parameter']]

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
        packet = "{dt_codes.PacketFields.FRAME_START}{cmd_str}{execute_cmd}"
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
    def _send_common_cmd(self, func: Union[runze_codes.CommonCmdCode, int],
                         param_value: int, wait: bool = True):
        b3, b4 = param_value.to_bytes(2, 'little')
        return self._send_common_cmd_raw(func, b3, b4, wait)

    def _send_common_cmd_raw(self, func: Union[runze_codes.CommonCmdCode, int],
                         b3: int, b4: int, wait: bool = True):
        """Send a common command frame to issue a command over Runze Protocol.
           Return a reply frame as a dict."""
        cmd_bytes = struct.pack(runze_codes.PacketFormat.SendCommon.value,
                                runze_codes.PacketFields.STX,
                                self.address, func, b3, b4,
                                runze_codes.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self._parse_runze_reply(self._send(packet,
                                                  protocol=Protocol.RUNZE))

    def _send_query(self, func: Union[runze_codes.CommonCmdCode, int],
                    param_value: int = 0x0000, wait: bool = True):
        """Send a query and return the reply."""
        b3, b4 = param_value.to_bytes(2, 'little')
        return self._send_common_cmd_raw(func, b3, b4, wait)

    def _send_factory_cmd(self, func: Union[runze_codes.FactoryCmdCode, int],
                          param_value, wait: bool = True):
        """Send a factory command frame to issue a command over Runze Protocol.
           Return a reply frame as a dict."""
        # Pack Factory Command password in the appropriate location.
        cmd_bytes = struct.pack(runze_codes.PacketFormat.SendFactory.value,
                                runze_codes.PacketFields.STX,
                                self.address, func,
                                FACTORY_CMD_PWD_CODE, param_value,
                                runze_codes.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self._parse_runze_reply(self._send(packet),
                                                 protocol=Protocol.RUNZE)

    def _parse_runze_reply(self, reply: bytes):
        """Parse reply sent over Runze protocol into respective fields."""
        reply_struct = struct.unpack(runze_codes.PacketFormat.Reply, reply)
        reply = dict(zip(runze_codes.CommonReplyFields, reply_struct))
        error = runze_codes.ReplyStatus(reply['status'])
        if error != runze_codes.ReplyStatus.NormalState:
            raise RuntimeError(f"Device replied with error code: {error.name}.")
        return reply

    def _send(self, packet: bytes, protocol: Protocol = Protocol.DT,
              wait: bool = True):
        """Send a message over the specified protocol and return the reply."""
        self.log.debug(f"Sending (hex): {packet.hex(' ')}")
        self.ser.write(packet)
        reply = bytes()
        start_time_s = perf_counter()
        while perf_counter() - start_time_s < self.__class__.LONG_TIMEOUT_S:
            try:
                if protocol == Protocol.RUNZE:
                    reply += self.ser.read(runze_codes.REPLY_NUM_BYTES)
                elif protocol == Protocol.DT:
                    reply += self.ser.read_until(
                        dt_codes.PacketFields.REPLY_FRAME_END.encode('ascii'))
                elif protocol == Protocol.OEM:
                    # check checksum.
                    raise NotImplementedError("OEM protocol not yet implemented.")
            except SerialException:
                pass
            if (len(reply) > 0) or not wait:
                break
        self.log.debug(f"Reply (hex): {reply.hex(' ')}")
        if len(reply) == 0:
            raise SerialException("No reply received from device.")
        return reply

