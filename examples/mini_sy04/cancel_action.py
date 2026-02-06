#!/usr/bin/env python3

import logging
import pprint
from time import sleep
from random import uniform

from runze_control.syringe_pump import MiniSY04

logging.basicConfig(level=logging.DEBUG)


# Constants
COM_PORT = "/dev/ttyUSB0"

# Connect to a single pump.
syringe_pump = MiniSY04(COM_PORT, address=0x00, syringe_volume_ul=20000)

logging.info(f"Syringe address: {syringe_pump.get_address()}")
logging.info(f"Syringe baud rate: {syringe_pump.get_rs232_baudrate()}")
logging.info("Resetting syringe.")
syringe_pump.reset_syringe_position()
logging.info(f"Moving plunger (in percent.)")
syringe_pump.move_absolute_in_percent(0) # wait = True
syringe_pump.set_speed_percent(20)
for i in range(10):
    sleep(0.5)
    logging.info(f"Starting 50% full-scale range move.")
    syringe_pump.move_absolute_in_percent(10, wait=False)
    print()
    sleep(uniform(0, 1)*0.25)
    while syringe_pump.is_busy():
        syringe_pump.halt()
        sleep(0.05)
    print()
    logging.info(f"Resuming movement.")
    syringe_pump.move_absolute_in_percent(0)
    logging.info(f"Syringe position: {syringe_pump.get_position_percent(): .3f}%")
    print()
    sleep(1)
