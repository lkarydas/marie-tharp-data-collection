"""Main file for Marie Tharp data collection."""

import os
import sys
import threading
import time
import logging
import signal

from absl import app
from absl import flags

import nmea_utils
import datetime
from datetime import timedelta
import colorama
from colorama import Fore, Style
import serial
import thread_utils
import timestamp_utils

FLAGS = flags.FLAGS

flags.DEFINE_string('output_dir', '.', 'Output directory for the data files.')
flags.DEFINE_bool('output_data', True, 'Whether or not to save the data.')
flags.DEFINE_boolean('save_debug_data', False,
                     'Saves a sample of data to a file and exits.')

DEBUG_DATA_SAMPLE_SIZE = 50  # Number of lines to save to debug file.

colorama.init()

# Lock to serialize console output.
lock = threading.Lock()

DEVICES = [
    {
        'device_name': 'Maretron NMEA USB Gateway',
        'short_name': 'maretron_nmea_gateway',
        'device_type': 'NMEA',
        'port': 'COM8',
        'baud_rate': 4800,
        'timeout': 1,
        'log_color': Fore.GREEN,
    },
    {
        'device_name': 'Garmin GPS 18x',
        'short_name': 'garmin_gps_18x',
        'device_type': 'NMEA',
        'port': 'COM3',
        'baud_rate': 4800,
        'timeout': 1,
        'log_color': Fore.RED,
    },
    {
        'device_name': 'Arduino Flowmeter',
        'short_name': 'flowmeter',
        'device_type': 'text',
        'port': 'COM9',
        'baud_rate': 9600,
        'timeout': 3,
        'log_color': Fore.BLUE,
    },
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


def open_port_and_log_data(device, timestamp):
  """Opens a serial port and logs the data."""
  port = device.get('port')
  log_color = device.get('log_color')
  device_name = device.get('device_name')
  device_short_name = device.get('short_name')
  baud_rate = device.get('baud_rate')
  timeout = device.get('timeout')
  device_type = device.get('device_type')

  logging.info(log_color + 'Trying to open port %s for %r' + Style.RESET_ALL,
               port, device_name)
  try:
    with serial.Serial(port, baud_rate, timeout=timeout) as ser:
      # When the `save_debug_data` flag is set, we save a sample of the data
      # to a file. Useful for debugging stuff later.
      if FLAGS.save_debug_data:
        debug_data_file_name = f'{timestamp}_{device_short_name}_debug.dat'
        with open(debug_data_file_name, 'ab') as f:
          for _ in range(DEBUG_DATA_SAMPLE_SIZE):
            f.write(ser.readline())
        return 0

      # A dictionary that keeps track of the timestamp that each message was
      # last written to the file.
      last_written = {}
      # Keep reading from serial indefinitely.
      output_file = os.path.join(FLAGS.output_dir,
                                 f'{timestamp}_{device_short_name}.dat')
      with open(output_file, 'a', encoding='utf-8') as f:
        while True:
          sentence = ser.readline().decode('ascii', errors='replace').strip()
          utc_now = datetime.datetime.utcnow()
          if not sentence:
            continue
          if device_type == 'NMEA':
            # Get the message code.
            code = nmea_utils.get_message_code(sentence)
            if not code:
              continue
            # Check if the NMEA sentence contains one of the messages we
            # want to keep.
            if code not in MESSAGES_TO_LOG:
              continue
            if (code in last_written and
                    utc_now - last_written[code] < timedelta(seconds=1)):
              continue
          print(log_color + sentence + Style.RESET_ALL)
          f.write(utc_now.strftime('%Y%m%dT%H%M%S%f') + ',' + sentence + '\n')
          f.flush()  # We need to flush after each write.
          if device_type == 'NMEA':
            last_written[code] = utc_now
          time.sleep(0.01)

  except serial.SerialException:
    logging.error(log_color + f'Could not open port {port}' + Style.RESET_ALL)
  logging.info(log_color + 'Thread %s: Finish.' +
               Style.RESET_ALL, device.get('device_name'))


def main(argv):
  """Main method for data collection."""
  del argv  # Unused.
  signal.signal(signal.SIGINT, signal_handler)
  format_string = "%(asctime)s %(threadName)s: %(message)s"
  logging.basicConfig(format=format_string, level=logging.INFO,
                      datefmt="%Y%m%dT%H%M%S")

  # The list of threads we are using, one per device.
  thread_list = []
  # Start each thread.
  utc_now = timestamp_utils.get_utc_timestamp()
  logging.info('Using timestamp: %s', utc_now)
  for index, device in enumerate(DEVICES):
    logging.info('Create and start thread %d for device %r.', index,
                 device.get('device_name'))
    thread = threading.Thread(target=open_port_and_log_data,
                              args=(device, utc_now,))
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
      logging.info('All threads are dead.')
      sys.exit(1)
    time.sleep(0.01)


if __name__ == "__main__":
  app.run(main)
