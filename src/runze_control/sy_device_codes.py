"""Syringe pump device codes."""
from enum import IntEnum

VALVE_ENCODER_MAX_STEPS = 2048
SYRINGE_ENCODER_MAX_STEPS = 6000
MOTOR_MAX_SPEED = 1000


class CommonCmdCode(IntEnum):
    """Codes to issue when querying/specifying the states of various settings
       via a Common Command frame."""
    # Queries
    GetAddress = 0x20  # Get Device Address
    GetRS232BaudRate = 0x21
    GetRS485BaudRate = 0x22
    GetCANBaudRate = 0x23
    GetPowerOnResetState = 0x2E
    GetCANDestinationAddress = 0x30
    GetMulticastChannel1Address = 0x70
    GetMulticastChannel2Address = 0x71
    GetMulticastChannel3Address = 0x72
    GetMulticastChannel4Address = 0x73
    GetCurrentChannelAddress = 0xAE
    GetCurrentVersion = 0x3F
    GetMotorStatus = 0x4A
    GetValveStatus = 0x4D
    # Commands
    MoveValveClockwiseMoveInSteps = 0x42  # Move valve clockwise a specified
                                          # number of encoder steps.
    MoveValveCounterClockwiseInSteps = 0x43  # Move valve counterclockwise a
                                             # specified number of encoder
                                             # steps.
    MoveValveToPort = 0x44  # Move valve to the port specified by B4. The
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
    GetSyringePosition = 0x66  # Get syringe pump address(?) TODO and possibly the position too?
    SyncSyringePumpPosition = 0x67  # TODO: what does this actually do?

