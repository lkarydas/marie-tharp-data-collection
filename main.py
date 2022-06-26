"""Main file for Marie Tharp data collection."""

import serial
import os
import time
import sys
import glob
import datetime
import time
import threading
import logging
import colorama
import signal
from colorama import Fore, Back, Style

colorama.init()

# Lock to serialize console output.
lock = threading.Lock()

DEVICES = [
    {
        'device_name': 'Maretron NMEA USB Gateway',
        'short_name': 'maretron_nmea_gateway',
        'port': 'COM8',
        'log_color': Fore.GREEN,
    },
    {
        'device_name': 'Garmin GPS 18x',
        'short_name': 'garmin_gps_18x',
        'port': 'COM3',
        'log_color': Fore.RED,
    }
]

# Only log a subset of the messages we care about.
MESSAGES_TO_LOG = [
  'DPT',  # Depth of water.
  'GGA',  # GPS fix data.
  'GSA',  # GPS DOP and active satelites.
  'GSV',  # Satelites in view.
]

def signal_handler(sig, frame):
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)

def open_serial_port(device):
  port = device.get('port')
  log_color = device.get('log_color')
  logging.info('Trying to open port %s' % port)
  try:
    with serial.Serial(port, 4800, timeout=1) as ser:
      # Discard the first 10 lines.
      for i in range(10):
        ser.readline()
      # Keep reading from serial indefinitely.
      while True:
        sentence = ser.readline().decode('ascii', errors='replace').strip()
        if not sentence:
          continue
        # Check if the NMEA sentence contains one of the messages we
        # want to keep.
        if sentence[3:6] in MESSAGES_TO_LOG:
          print(log_color + sentence + Style.RESET_ALL)
        time.sleep(0.01)

  except serial.SerialException as e:
    logging.error(log_color + 'Could not open port %s' % port + Style.RESET_ALL)


def thread_function(device):
    log_color = device.get('log_color')
    logging.info("Thread %s: starting", device.get('device_name'))
    open_serial_port(device)
    logging.info("Thread %s: finishing", device.get('device_name'))


def main():
    signal.signal(signal.SIGINT, signal_handler)
    format = "%(asctime)s %(threadName)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%Y%m%dT%H%M%S")

    # The list of threads we are using, one per device.
    threads = list()
    # Start each thread.
    for index, device in enumerate(DEVICES):
        logging.info("Main    : create and start thread %d.", index)
        t = threading.Thread(target=thread_function, args=(device, ))
        t.name = device.get('short_name')
        # Making the threads daemons means that they will be killed when
        # the main program is killed.
        t.daemon = True
        threads.append(t)
        t.start()
    
    # Infinate loop to keep the main thread alive.
    while True:
      time.sleep(0.01)


if __name__ == "__main__":
    main()
