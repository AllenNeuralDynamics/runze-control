#!/usr/bin/env python3

import logging
import pprint
import random
from time import sleep

from runze_control.multichannel_syringe_pump import SY01B

from runze_control.runze_device import get_protocol, set_protocol
from runze_control.protocol import Protocol

# Uncomment for some prolific log statements.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(
    logging.Formatter(fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'))


# Constants
COM_PORT = "/dev/ttyUSB0"

#print(get_protocol(COM_PORT, 9600))
#print(set_protocol(COM_PORT, 9600, Protocol.RUNZE))

# Connect to a single pump.
m_channel_pump = SY01B(COM_PORT, baudrate=9600,
                       position_count=9, syringe_volume_ul=5000)
print(f"Syringe address: {m_channel_pump.get_address()}")
print(f"Syringe baud rate: {m_channel_pump.get_rs232_baudrate()}")
print(f"Firmware Version: {m_channel_pump.get_firmware_version()}")
print("Resetting syringe.")
m_channel_pump.reset_syringe_position()
sleep(0.5)

percentages = [100, 25, 50, 0]
for percent in percentages:
    print(f"Moving plunger to {percent}% travel range.")
    m_channel_pump.move_absolute_in_percent(percent)
    sleep(0.5)

position = random.randint(1, 9)
print(f"Moving valve to position: {position}")
m_channel_pump.move_valve_to_position(position)
sleep(0.5)
position = random.randint(1, 9)
print(f"Moving valve to position: {position}")
m_channel_pump.move_valve_to_position(position)
sleep(0.5)


microliters= 2500
print(f"Withdrawing {microliters}[uL]")
m_channel_pump.withdraw(microliters)
print(f"Dispensing {microliters}[uL]")
m_channel_pump.dispense(microliters)

