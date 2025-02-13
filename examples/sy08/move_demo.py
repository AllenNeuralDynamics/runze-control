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
syringe_pump = SY08(COM_PORT, address=0x00, syringe_volume_ul=25000)
syringe_pump.reset_syringe_position()

syringe_pump.aspirate(1000)
sleep(1)
syringe_pump.aspirate(1000)
sleep(1)
syringe_pump.dispense(1500)
sleep(1)
syringe_pump.dispense(500)
