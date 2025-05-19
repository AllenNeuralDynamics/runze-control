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
m_channel_pump = SY01B(COM_PORT, baudrate=9600, address=0x00,
                     position_count=9, syringe_volume_ul=5000)
#syringe_pump = None
#for address in range(0, 0xFF+1):
#    try:
#        # auto-detect baud rate.
#        syringe_pump = SY01B(COM_PORT, baudrate=9600, address=address)
#        break
#    except Exception:
#        pass
print(f"Syringe address: {m_channel_pump.get_address()}")
print(f"Syringe baud rate: {m_channel_pump.get_rs232_baudrate()}")
print("Resetting syringe.")
m_channel_pump.reset_syringe_position()
sleep(0.5)
#print(f"Moving plunger (in percent.)")
#syringe_pump.move_absolute_in_percent(25)

position = random.randint(1, 9)
print(f"Moving valve to position: {position}")
m_channel_pump.move_valve_to_position(position)
sleep(0.5)
position = random.randint(1, 9)
print(f"Moving valve to position: {position}")
m_channel_pump.move_valve_to_position(position)
sleep(0.5)


#print(f"Withdrawing 10uL")
#syringe_pump.withdraw(10)
#print(f"Dispensing 10uL")
#syringe_pump.dispense(10)

#print(f"Syringe position is now: {syringe_pump.get_position_steps()}")
#syringe_pump.move_absolute_in_percent(0)
