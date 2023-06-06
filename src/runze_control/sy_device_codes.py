"""Syringe pump device codes."""
from enum import Enum

VALVE_ENCODER_MAX_STEPS = 2048
SYRINGE_ENCODER_MAX_STEPS = 6000
MOTOR_MAX_SPEED = 1000


class CommonQueryCode(Enum):
    Address = 0x20
    RS232BaudRate = 0x21
    RS485BaudRate = 0x22
    CANBaudRate = 0x23
    ResetUponPowerUpState = 0x2E
    CANDestinationAddress = 0x30
    MulticastChannel1Address = 0x70
    MulticastChannel2Address = 0x71
    MulticastChannel3Address = 0x72
    MulticastChannel4Address = 0x73
    CurrentChannelAddress = 0xAE
    CurrentVersion = 0x3F
    MotorStatus = 0x4A
    ValveStatus = 0x4D


class CommonCmdCode(Enum):
    MoveValveClockwiseMoveInSteps  = 0x42  # Move valve clockwise a specified
                                           # number of encoder steps.
    MoveValveCounterClockwiseInSteps = 0x43  # Move valve counterclockwise a
                                             # specified number of encoder
                                             # steps.
    MoveValvetoPort = 0x44  # Move valve to the port specified by B4. The
                            # approach direction is determined automatically.
                            # Values range from 1-N, where N is the number of
                            # ports.
    ResetValvePosition = 0x4C  # Move valve to reset position and stop.
    ResetSyringePosition = 0x45  # Move syringe plunger to the start of travel.
    ForcedReset = 0x4F  # Move syringe plunger to the start of travel and
                        # back off by a small amount (improves service life.)
    Halt = 0x49  # immediately stop moving the syringe and valve rotor.
    SetSpeed = 0x4B  # TODO: plunger or valve stator speed?
    MovePlungerAbsolute = 0x4E  # Move syringe plunger to an absolute position
                                # in steps [0-6000].
    GetSyringePostion = 0x66  # Get syringe pump address(?) TODO and possibly the position too?
    SyncSyringePumpPosition = 0x67  # TODO: what does this actually do?

