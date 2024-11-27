#!/usr/bin/env python3

import logging
import pprint
from time import sleep

from runze_control.syringe_pump import SY08

# Uncomment for some prolific log statements.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(
    logging.Formatter(fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'))


# Constants
COM_PORT = "/dev/ttyUSB0"

# Connect to a single pump.
#syringe_pump = SY01B(COM_PORT, baudrate=9600, address=0x31)
#syringe_pump = SY08(COM_PORT, address=0x20)
#syringe_pump = SY08(COM_PORT, address=0x31)
syringe_pump = SY08(COM_PORT, address=0x00, syringe_volume_ul=25000)

print(f"Syringe address: {syringe_pump.get_address()}")
print(f"Syringe baud rate: {syringe_pump.get_rs232_baudrate()}")
print("Resetting syringe.")
syringe_pump.reset_syringe_position()
print(f"Moving plunger (in percent.)")
syringe_pump.move_absolute_in_percent(0) # wait = True

sleep(0.5)
print(f"Starting 50% full-scale range move.")
syringe_pump.move_absolute_in_percent(50, wait=False)
sleep(1.0)
print(f"Halting.")
syringe_pump.halt()
print(f"Syringe position: {syringe_pump.get_position_ul()} [uL]")
sleep(1.0)
print(f"Resuming movement.")
syringe_pump.move_absolute_in_percent(50)
print(f"Syringe position: {syringe_pump.get_position_ul()} [uL]")
