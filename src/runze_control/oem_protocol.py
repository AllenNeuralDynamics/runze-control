"""Runze Fluid device codes common across devices."""

from enum import IntEnum


class PacketFields(IntEnum):
    """OEM Protocol Packet Fields."""
    STX = 0x02
    ETX = 0x03
    DEFAULT_SEQUENCE_NUMBER = 0x31
