"""Rotary Valve driver"""
from __future__ import annotations
from runze_control.protocol import Protocol
from runze_control.runze_device import RunzeDevice
from runze_control.protocol_codes import rotary_valve_codes
from typing import Union


class RotaryValve(RunzeDevice):

    def __init__(self, com_port: str, baudrate: int = None, address: int = 0x31,
                 protocol: Union[str, Protocol] = Protocol.RUNZE,
                 position_count: int = None, position_map: dict = None,
                 **kwargs):
        # Pass along unused kwargs to satisfy diamond inheritance.
        super().__init__(com_port=com_port, baudrate=baudrate,
                         address=address, protocol=protocol, **kwargs)
        self.codes = rotary_valve_codes
        self.position_count = position_count
        self.position_map = position_map


    def move_to_position(self, position: Union[str, int]):
        pass

    def move_clockwise_to_position(self, position: Union[str, int]):
        pass

    def move_counterclockwise_to_position(self, position: Union[str, int]):
        pass
