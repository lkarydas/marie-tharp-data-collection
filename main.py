"""Main file for Marie Tharp data collection."""

import pynmea2
import serial
import os
import time
import sys
import glob
import datetime

def main():
  
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