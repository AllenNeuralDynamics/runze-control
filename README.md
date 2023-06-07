python serial interfaces to various devices by Runze Fluid and Aurora Pro Scientific.

## Supported Devices:
* Multiport Selector Valve **In Progress**
    * QHF-SV07 series datasheet [pdf](https://www.runzefluid.com/uploads/file/sv-07-multiport-selector-valve-manual-v1-4.pdf)
* Syringe Pump **In Progress**
    * ZSB-SY01B series datasheet [pdf](https://www.runzefluid.com/uploads/file/sy-01b-user's-manual-v1-0.pdf)


## Getting Started
````python
from runze_control.syringe_pump import SY01B
````

If you know the baudrate of your device, you can create an instance with:
````python
syringe_pump = SY01B("COM3", 115200) # Create a device instance with a known
                                     # baudrate and default address 0x00.
````

If you don't know the baudrate, you can create an instance with:
````python
syringe_pump = SY01B("COM3") # Create a device instance with unknown
                             # baudrate and default address 0x00.
````
The above command will scan through all valid baudrates until it successfully
connects to a device.

The factory default device address is set to 0x00.
If the device's address has been set to a different address, you can specify it
with:
````python
syringe_pump = SY01B("COM3", bus_address=0x01) # Create a device instance with
                                               # an unknown baudrate and
                                               # address 0x01.
````

From here, various commands exist such as:
````python
syringe_pump.set_port(1)  # Select valve port 1.
syringe_pump.withdraw(1000)  # Withdraw 1000[uL] from the current port.
syringe_pump.set_port(10)  # Select valve port 10
syringe_pump.dispense(1000)  # Dispense 1000[uL] to the current port.
````

A host of other commands exist to provision the syringe pump (and all other devices) with default power-up settings.
For more details, see the [documentation]().

## Logging
All hardware transactions are logged via an instance-level logger.
No handlers are attached, but you can display them with this boilerplate code:
````python
import logging

# Send log messages to stdout so we can see every outgoing/incoming msg.
# Only display messages from this package.
class LogFilter(logging.Filter):
    def filter(self, record):
        return record.name.split(".")[0].lower() in ['runze_control']

fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(logging.Formatter(fmt=fmt))
logger.handlers[-1].addFilter(LogFilter())

# Now, create a device instance as usual and issue some commands to it.
````
