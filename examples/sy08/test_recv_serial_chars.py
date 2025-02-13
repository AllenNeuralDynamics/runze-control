#!/usr/bin/env python3
from serial import Serial, SerialException
import logging

DEFAULT_TIMEOUT_S = 0.5  # Default communication timeout in seconds.
VALID_RS232_AND_RS485_BAUDRATES_BPS = [9600, 19200, 38400, 57600, 115200]
VALID_PORT_COUNT = [6, 9, 12]

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(
    logging.Formatter(fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'))

com_port = "/dev/ttyUSB0"
br = 9600

ser = Serial(com_port, br, timeout=1.0)
try:
    while True:
        reply = ser.read(1)
        if len(reply):
            logging.debug(f"Reply (hex): {reply.hex(' ')}")
except KeyboardInterrupt:
    ser.close()


