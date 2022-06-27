"""Main file for Marie Tharp data collection."""

import sys
import threading
import time
import logging
import signal

import serial
import colorama
from colorama import Fore, Style

import thread_utils

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
  """Signal handler."""
  del sig, frame
  print('SIGINT or CTRL-C detected. Exiting gracefully')
  sys.exit(0)


def open_serial_port(device):
  """Opens a serial port and logs the data."""
  port = device.get('port')
  log_color = device.get('log_color')
  logging.info(log_color + 'Trying to open port %s' + Style.RESET_ALL, port)
  try:
    with serial.Serial(port, 4800, timeout=1) as ser:
      # Discard the first 10 lines.
      for _ in range(10):
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

  except serial.SerialException:
    logging.error(log_color + 'Could not open port %s' %
                  port + Style.RESET_ALL)


def thread_function(device):
  """The main method for each thead."""
  log_color = device.get('log_color')
  logging.info(log_color + 'Thread %s: Start.' +
               Style.RESET_ALL, device.get('device_name'))
  open_serial_port(device)
  logging.info(log_color + 'Thread %s: Finish.' +
               Style.RESET_ALL, device.get('device_name'))


def main():
  """Main method."""
  signal.signal(signal.SIGINT, signal_handler)
  format_string = "%(asctime)s %(threadName)s: %(message)s"
  logging.basicConfig(format=format_string, level=logging.INFO,
                      datefmt="%Y%m%dT%H%M%S")

  # The list of threads we are using, one per device.
  thread_list = list()
  # Start each thread.
  for index, device in enumerate(DEVICES):
    logging.info('Create and start thread %d for device %r.', index,
                 device.get('device_name'))
    thread = threading.Thread(target=thread_function, args=(device, ))
    thread.name = device.get('short_name')
    # Making the threads daemons means that they will be killed when
    # the main program is killed.
    thread.daemon = True
    thread_list.append(thread)
    thread.start()

  # Infinate loop to keep the main program going, as long at least one
  # of the other threads are still alive.
  while True:
    if thread_utils.are_all_threads_dead(thread_list):
      logging.fatal('All threads are dead.')
      sys.exit(1)
    time.sleep(0.01)


if __name__ == "__main__":
  main()
