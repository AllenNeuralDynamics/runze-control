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
syringe_pump.reset_syringe_position()

#logger.info(f"Changing speed.")
syringe_pump.set_speed_percent(10)
logger.info(f"Moving with new speed.")
syringe_pump.move_absolute_in_percent(5) # wait = True
logger.info(f"Changing speed.")
syringe_pump.set_speed_percent(60)
logger.info(f"Moving with new speed.")
syringe_pump.move_absolute_in_percent(0) # wait = True
