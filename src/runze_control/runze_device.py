"""Syringe Pump Driver."""
from functools import reduce, wraps
from runze_control.protocol_codes import common_codes
from runze_control.protocol import *
from runze_control.runze_protocol import FACTORY_CMD_PWD_CODE
from runze_control import runze_protocol
from runze_control import dt_protocol
from runze_control import oem_protocol
from serial import Serial, SerialException
from typing import Union
from time import perf_counter
import logging
import struct

logger = logging.getLogger(__name__)


def get_protocol(com_port: str, baudrate: int = 9600):
    ser = Serial(com_port, baudrate, timeout=0.1)
    ser.write(REQUEST_PROTOCOL_MODE)
    reply = ser.read(32) # Read up to 32 bytes
    return ProtocolReply(reply)


def set_protocol(com_port: str, baudrate: int = 9600,
                 protocol: Union[str, Protocol] = Protocol.RUNZE):
    set_protocol_cmd = SetProtocol[Protocol(protocol).name]
    ser = Serial(com_port, baudrate, timeout=0.1)
    ser.write(set_protocol_cmd)
    logger.warning(f"Protocol changed to {protocol}. Device requires power "
                   f"cycle for changes to take effect.")


class RunzeDevice:
    """Base class for a generic Runze Fluid device exposing commands common
    to all devices."""

    DEFAULT_TIMEOUT_S = 0.25  # Default communication timeout in seconds.
    LONG_TIMEOUT_S = 60.0  # Default communication timeout in seconds.
                           # This needs to be a bit long since some device
                           # behavior (syringes moving) take several seconds
                           # to complete before issuing their reply.
    VALID_BAUDRATES = \
    {
        Protocol.DT: [9600, 38400],
        Protocol.RUNZE: [9600, 19200, 38400, 57600, 115200]
    }

    RUNZE_DEFAULT_ADDRESS = 0x00 # max: 127 (128 devices).
    ASCII_DEFAULT_ADDRESS = 0x31 # ASCII: '0' max: 0x3F (16 devices).

    def __init__(self, com_port: str, baudrate: int = None,
                 address: Union[int, str] = None,
                 protocol: Union[str, Protocol] = Protocol.RUNZE):
        """Init. Connect to a device with the specified address via an
           RS232 or RS485 interface.

        :param com_port: com port to connect to.
        :param baudrate: device baud rate. Factory default is 9600, but can be
            changed to standard baud rates up through 115200bps via serial
            command.

            .. note::
               Runze Protocol and ASCII Protocol have different valid baud
               rates.

        :param address: specify the device to connect to.

            .. note::
               In Runze Protocol under an RS232 connection, this value can
               be omitted (left as None), and the device will discover it
               automatically.

            .. warning::
                Runze and ASCII protocols have distinct valid addresses and
                address ranges. Address will be interpreted per the `protocol`
                paramter.

            .. note::
               The device address can be specified on the physical device itself
               for devices that have a rotary switch. Switch position 0
               corresponds to device 1 at Runze protocol address 0 or ASCII
               protocol address '1'.

        :param protocol: protocol over which to send commands to the device
            ("RUNZE" or "DT" [aka: ASCII]). Protocol must match the one
            specified on the device, but it can be changed after connecting to
            it.

        """
        self.address = address
        self.protocol = Protocol(protocol)
        self.ser = None
        logger_name = self.__class__.__name__ + (f".{com_port}")
        self._timeout_s = self.__class__.DEFAULT_TIMEOUT_S
        self.log = logging.getLogger(logger_name)
        self.codes = common_codes  # Can be overwritten in child class.
        self.cmd_send_time_s = None # Time last command was sent to the device
                                    # before reply was received or None if no
                                    # issued command is waiting for a reply.
        # if baudrate is unspecified, try all of them before giving up.
        baudrates = [baudrate] if baudrate is not None \
                    else RunzeDevice.VALID_BAUDRATES[self.protocol]
        # Try all valid baud rates or the one specified.
        try:
            for br in baudrates:
                try:
                    log_msg_suffix = "." if address is None else \
                        f" on address: 0x{address:02x}."
                    self.log.debug(f"Connecting to device on port: {com_port}"
                                   f" at {br}[bps]" + log_msg_suffix)
                    # We will manually apply the timeout in the _send method.
                    self.ser = Serial(com_port, br, timeout=0)
                    self.ser.reset_input_buffer()
                    self.ser.reset_output_buffer()
                    # Test link by issuing a protocol-dependent dummy command.
                    if address is None:
                        self.log.debug("Discovering device address.")
                        self.address = 0 # Specify a temp dummy address.
                        self.address = self.get_address()
                    if self.protocol == Protocol.RUNZE and (address != None):
                        device_address = self.get_address()
                        if self.address != device_address:
                            raise ValueError(f"Device address is incorrectly "
                                f"specified! specified address: {address}. "
                                f"device's actual address: {device_address}.")
                    elif self.protocol == Protocol.DT:
                        raise NotImplementedError
                    elif self.protocol == Protocol.OEM:
                        raise NotImplementedError
                    break
                except SerialException as e:
                    self.cmd_send_time_s = None # Forget about last msg sent.
                    # Raise exception only if we've tried all valid baud rates.
                    self.log.debug(f"Connecting failed.")
                    if br == baudrates[-1]:
                        raise
        except SerialException as e:
            self.log.error("Error: could not open connection to device. "
                "Is it plugged in and powered on? Is another program using it?")
            raise
        # Restore long timeout (required for long syringe moves.)
        self._timeout_s = self.__class__.LONG_TIMEOUT_S

    def get_firmware_version(self):
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query_runze(self.codes.CommonCmd.GetFirmwareVersion)
            b3b4 = reply['parameter'].to_bytes(2, 'little')
            b3 = b3b4[0]
            b4 = b3b4[1]
            return float(f"{b3}.{b4}")
        elif self.protocol == Protocol.DT:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def get_protocol(self):
        """Get the protocol that the device is set to communicate in."""
        raise NotImplementedError
        #reply = self.ser.send()
        #if reply == ProtocolReply.RUNZE:
        #    return Protocol.RUNZE
        #elif reply == ProtocolReply.DT:
        #    return Protocol.DT

    def set_address(self, address: int):
        """Set the device for this bus (only necessary for RS485)."""
        pass

    def get_address(self):
        """ Get the device address. Under Runze Protocol, any device
        that receives this command will respond with its address even if it is
        incorrect.
        """
        self.log.debug("Requesting address.")
        if self.protocol == Protocol.RUNZE:
            reply = self._send_query_runze(self.codes.CommonCmd.GetAddress)
            return reply['parameter']
        elif self.protocol == Protocol.DT:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def get_serial_number(self):
        if self.protocol != Protocol.DT:
            raise NotImplementedError
        self._send_cmd_dt("?202") # FIXME: use enums.

    def set_multicast_address(self, multicast_channel: int, address: int):
        """Set the multicast address for this bus (only necessary for RS485).
        Specifying multiple valves with the same multicast address enables
        sending the same commands to groups of valves simultaneously.
        """
        pass

    def get_rs232_baudrate(self):
        reply = self._send_query_runze(self.codes.CommonCmd.GetRS232Baudrate)
        return runze_protocol.RS232BaudrateReply[reply['parameter']]

    def get_rs485_baudrate(self):
        reply = self._send_query_runze(self.codes.CommonCmd.GetRS485Baudrate)
        return runze_protocol.RS485BaudrateReply[reply['parameter']]

    def get_can_baudrate(self):
        raise NotImplementedError

    def is_busy(self):
        """True if a command was previously issued without waiting, and the
        reply has not yet been received."""
        # Child classes may need to query another field if this class is not
        # strictly waiting for a command to complete.
        if self.cmd_send_time_s is None:
            return False
        # Check if the last command we sent has issued a reply. Don't block.
        reply = self._parse_runze_reply(self._get_reply(protocol=self.protocol,
                                                        wait=False))
        if reply is None:
            return True # No reply has been received yet.
        return False

    def wait_for_reply(self, force: bool = False):
        return self._parse_runze_reply(self._get_reply(protocol=self.protocol,
                                                       force=force))

    def _send_cmd_dt(self, cmd_str: str, execute: bool = True):
        """Send a command over DT protocol and return the reply."""
        cmd_str_bytes = cmd_str.encode('ascii')
        cmd_str_bin_encoding = "B"*len(cmd_str_bytes)
        encoding = f"<B{cmd_str_bin_encoding}B"
        cmd_bytes = struct.pack(encoding,
                                dt_protocol.PacketFields.FRAME_START,
                                self.address.encode('ascii'),
                                *cmd_str_bytes,
                                dt_protocol.PacketFields.FRAME_END)
        execute_cmd = "R" if execute else ""
        packet = "{dt_protocol.PacketFields.FRAME_START}{cmd_str}{execute_cmd}"
        return self._send(packet.encode("ASCII"), protocol=Protocol.DT)

    def _send_cmd_oem(self, cmd_str: str, execute: bool = True):
        """Send a command over oem protocol and return the reply."""
        if execute:
            cmd_str += "R"
        cmd_str_bytes = cmd_str.encode('ascii')
        cmd_str_bin_encoding = "B"*len(cmd_str_bytes)
        encoding = f"<B{cmd_str_bin_encoding}B"
        cmd_bytes = struct.pack(encoding,
                                oem_protocol.PacketFields.STX,
                                self.address,
                                oem_protocol.PacketFields.DEFAULT_SEQUENCE_NUMBER
                                *cmd_str_bytes,
                                oem_protocol.PacketFields.ETX)
        checksum = reduce(lambda a, b: a ^ b, cmd_bytes)  # XOR
        packet = cmd_bytes + checksum.to_bytes(1, 'little')
        return self._send(packet)

    def _send_common_cmd_runze(self, func: Union[common_codes.CommonCmd, int],
                               param_value: int = 0, wait: bool = True,
                               force: bool = False):
        """Send a common command over Runze Protocol and return the reply."""
        b3, b4 = param_value.to_bytes(2, 'little')
        return self._send_common_cmd_frame_runze(func, b3, b4, wait, force)

    def _send_query_runze(self, func: Union[common_codes.CommonCmd, int],
                          param_value: int = 0x0000, wait: bool = True,
                          force: bool = False):
        """Send a query over Runze Protocol and return the reply."""
        b3, b4 = param_value.to_bytes(2, 'little')
        return self._send_common_cmd_frame_runze(func, b3, b4, wait, force)

    def _send_factory_cmd_runze(self, func: Union[common_codes.FactoryCmd, int],
                                param_value, wait: bool = True, force: bool = False):
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
        return self._parse_runze_reply(self._send(packet,
                                                  protocol=Protocol.RUNZE,
                                                  wait=wait,
                                                  force=force))

    def _send_common_cmd_frame_runze(self, func: Union[common_codes.CommonCmd, int],
                                     b3: int, b4: int, wait: bool = True,
                                     force: bool = False):
        """Send a common command frame to issue a command over Runze Protocol.
           Return a reply frame as a dict."""
        cmd_bytes = struct.pack(runze_protocol.PacketFormat.SendCommon.value,
                                runze_protocol.PacketFields.STX,
                                self.address, func, b3, b4,
                                runze_protocol.PacketFields.ETX)
        checksum = sum(bytearray(cmd_bytes))
        packet = cmd_bytes + checksum.to_bytes(2, 'little')
        return self._parse_runze_reply(self._send(packet,
                                                  protocol=Protocol.RUNZE,
                                                  wait=wait,
                                                  force=force))

    def _parse_runze_reply(self, reply: bytes):
        """Parse reply sent over Runze protocol into respective fields."""
        if not len(reply):
            return None
        reply_struct = struct.unpack(runze_protocol.PacketFormat.Reply, reply)
        parsed_reply = dict(zip(runze_protocol.CommonReplyFields, reply_struct))
        error = runze_protocol.ReplyStatus(parsed_reply['status'])
        #self.log.debug(f"parsed: {parsed_reply}, status: {error.name}")
        if error != runze_protocol.ReplyStatus.NormalState:
            raise RuntimeError(f"Device replied with error code: {error.name}.")
        return parsed_reply

    def _send(self, packet: bytes, protocol: Protocol = Protocol.DT,
              wait: bool = True, force: bool = False):
        """Send a message over the specified protocol and return the reply."""
        if self.cmd_send_time_s is not None and not force:
            raise RuntimeError("Cannot issue a command while the previous "
                               "command has not yet replied.")
        self.log.debug(f"Sending (hex): {packet.hex(' ')}")
        self.ser.write(packet)
        self.cmd_send_time_s = perf_counter()
        if not wait:
            self.log.debug("Not waiting for reply from device.")
            return bytes()  # Empty reply
        # Every command issues a reply. Get it.
        reply = self._get_reply(protocol, wait)
        if len(reply) == 0:
            raise SerialException("No reply received from device.")
        return reply

    def _get_reply(self, protocol: Protocol = Protocol.DT, wait: bool = True,
                   force: bool = False):
        """Retrieve the reply from a previously-issued command.
        If wait, wait up to the timeout period to retrieve the reply.
        Otherwise return immediately with an empty reply if reply has not been
        received.
        """
        if self.cmd_send_time_s is None and not force:
            raise SerialException("Cannot retrieve a reply. "
                                  "No command has been issued.")
        reply = bytes()
        while True:
            # pyseral Timeout is zero, so these calls return immediately if no reply.
            try:
                if protocol == Protocol.RUNZE:
                    reply += self.ser.read(runze_protocol.REPLY_NUM_BYTES)
                elif protocol == Protocol.DT:
                    reply += self.ser.read_until(
                        dt_protocol.PacketFields.REPLY_FRAME_END.encode('ascii'))
                elif protocol == Protocol.OEM:
                    # check checksum.
                    raise NotImplementedError("OEM protocol not yet implemented.")
            except SerialException:
                pass
            if len(reply) or not wait:
                break
            if perf_counter() - self.cmd_send_time_s >= self._timeout_s:
                break
        self.log.debug(f"Reply (hex): {reply.hex(' ')}")
        if len(reply):
            self.cmd_send_time_s = None  # Cmd-reply loop finished. Unassign.
        return reply
