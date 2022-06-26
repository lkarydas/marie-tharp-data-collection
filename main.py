"""Main file for Marie Tharp data collection."""

import pynmea2
import serial
import os
import time
import sys
import glob
import datetime


def _scan_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        patterns = ('/dev/tty[A-Za-z]*', '/dev/ttyUSB*')
        ports = [glob.glob(pattern) for pattern in patterns]
        ports = [item for sublist in ports for item in sublist]  # flatten
    elif sys.platform.startswith('darwin'):
        patterns = ('/dev/*serial*', '/dev/ttyUSB*', '/dev/ttyS*')
        ports = [glob.glob(pattern) for pattern in patterns]
        ports = [item for sublist in ports for item in sublist]  # flatten
    else:
        raise EnvironmentError('Unsupported platform')
    return ports

def main():
  print("Hello World!")

  ports = _scan_ports()
  print('Found %i serial ports.' % len(ports))

  # Hardcode to COM8 for now.
  port = 'COM8'


  print('Trying port %s' % port)
  with serial.Serial(port, 4800, timeout=1) as ser:
      # 'warm up' with reading some input.
      # TODO(laz): Do we really need this?
      for i in range(10):
          ser.readline()
      # Try to parse (will throw an exception if input is not valid NMEA).
      pynmea2.parse(ser.readline().decode('ascii', errors='replace'))
  
      while True:
          line = ser.readline()
          print(line.decode('ascii', errors='replace').strip())

if __name__ == "__main__":
    main()