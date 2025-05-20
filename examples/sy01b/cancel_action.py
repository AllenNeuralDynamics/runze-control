#!/usr/bin/env python3

import logging
import pprint
from time import sleep

from runze_control.multichannel_syringe_pump import SY01B

# Uncomment for some prolific log statements.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(
    logging.Formatter(fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'))


# Constants
COM_PORT = "/dev/ttyUSB0"

# Connect to a single pump.
syringe_pump = SY01B(COM_PORT, address=0x00, syringe_volume_ul=5000)

logger.info(f"Syringe address: {syringe_pump.get_address()}")
logger.info(f"Syringe baud rate: {syringe_pump.get_rs232_baudrate()}")
logger.info("Resetting syringe.")
syringe_pump.reset_syringe_position()
logger.info(f"Moving plunger (in percent.)")
syringe_pump.move_absolute_in_percent(25) # wait = True

sleep(0.5)
logger.info(f"Starting 50% full-scale range move.")
syringe_pump.move_absolute_in_percent(50, wait=False)
logger.info(f"is syringe busy? -> {'yes' if syringe_pump.is_busy() else 'no'}")
logger.info(f"is syringe busy? -> {'yes' if syringe_pump.is_busy() else 'no'}")
logger.info(f"is syringe busy? -> {'yes' if syringe_pump.is_busy() else 'no'}")
sleep(0.25)
logger.info("Halting.")
syringe_pump.halt()
logger.info(f"Syringe position: {syringe_pump.get_position_percent()}%")
logger.info(f"Syringe position: {syringe_pump.get_position_percent()}%")
logger.info(f"Syringe position: {syringe_pump.get_position_percent()}%")
logger.info(f"Syringe position: {syringe_pump.get_position_percent()}%")
sleep(1.0)
logger.info(f"Resuming movement.")
syringe_pump.move_absolute_in_percent(50, wait=True)
#logger.info(f"Syringe position: {syringe_pump.get_position_percent()}%")
logger.info(f"Syringe position: {syringe_pump.get_position_percent()}%")
