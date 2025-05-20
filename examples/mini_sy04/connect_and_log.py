#!/usr/bin/env python3

import logging
import pprint
from time import sleep

from runze_control.syringe_pump import MiniSY04

# Uncomment for some prolific log statements.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(
    logging.Formatter(fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'))


# Constants
COM_PORT = "/dev/ttyUSB0"

# Connect to a single pump.
syringe_pump = MiniSY04(COM_PORT, address=0x00, syringe_volume_ul=20000)
print(f"Syringe address: {syringe_pump.get_address()}")
print(f"Syringe baud rate: {syringe_pump.get_rs232_baudrate()}")
print(f"Firmware Version: {syringe_pump.get_firmware_version()}")
print("Resetting syringe.")
syringe_pump.reset_syringe_position()
sleep(1.0)
print(f"Freshly-reset syringe position is: {syringe_pump.get_position_steps()}")

print(f"Withdrawing 10uL")
syringe_pump.withdraw(2000)
sleep(1.0)
print(f"Syringe position is now: {syringe_pump.get_position_steps()}")
sleep(1.0)
print(f"Dispensing 10uL")
syringe_pump.dispense(2000)
sleep(1.0)
print(f"Syringe position is now: {syringe_pump.get_position_steps()}")
#syringe_pump.move_absolute_in_percent(0)
