"""Syringe pump device codes."""
from enum import Enum

VALVE_ENCODER_MAX_STEPS = 2048
SYRINGE_ENCODER_MAX_STEPS = 6000
MOTOR_MAX_SPEED = 1000

FACTORY_CMD_PWD_CODE = 0xFFEEBBAA

REPLY_END_OF_FRAME = 0xDD
REPLY_NUM_BYTES = 8

class PacketFormat(Enum):
    SendCommon = "<BBBBBBH"
    SendFactory = "<BBBBBBBBBBBBH"
    Reply = "<BBBBBBH"


class FactoryCmdCode(Enum):
    pass


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
    ValveClockwiseMoveSteps  = 0x42
    ValveCounterClockwiseMoveSteps = 0x43
    ResetSyringePosition = 0x45  # move the syringe to the start of travel.
    Halt = 0x49  # immediately stop moving the syringe and valve rotor.
    SetSpeed = 0x4B  # TODO: plunger or valve stator speed?
    GetSyringePostion = 0x66  # Get syringe pump address(?) TODO and possibly the position too?
    SyncSyringePumpPosition = 0x67  # TODO: what does this actually do?
    
    

