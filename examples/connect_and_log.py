#!/usr/bin/env python3

import logging
import pprint
from time import sleep

from runze_control.syringe_pump import SY01B

# Uncomment for some prolific log statements.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(
    logging.Formatter(fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'))


# Constants
COM_PORT = "/dev/ttyUSB0"

# Connect to a single pump.
syringe_pump = SY01B(COM_PORT) # Bus address 0x00. auto-detect baud rate.
print(f"Syringe baud rate: {syringe_pump.get_rs232_baud_rate()}")
print(f"Syringe position: {syringe_pump.get_syringe_position()}")
