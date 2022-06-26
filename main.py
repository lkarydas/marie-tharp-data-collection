"""Main file for Marie Tharp data collection."""

import pynmea2
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


def open_serial_port(device):
    port = device.get('port')
    log_color = device.get('log_color')
    logging.info('Trying to open port %s' % port)
    try:
      with serial.Serial(port, 4800, timeout=1) as ser:
          for i in range(10):
              ser.readline()
          # Read 10 lines and stop.
          for i in range(10):
              line = ser.readline()
              if not line:
                continue
              print(log_color + line.decode('ascii', errors='replace').strip() + Style.RESET_ALL)
              try:
                msg = pynmea2.parse(ser.readline().decode(
                    'ascii', errors='replace'))
                print(log_color + 'Message: %s' % msg  + Style.RESET_ALL)
              except pynmea2.nmea.ChecksumError:
                logging.error(log_color + 'Checksum error!' + Style.RESET_ALL)
              except TypeError:
                logging.error(log_color + 'TypeError!' + Style.RESET_ALL)
    except serial.SerialException as e:
      logging.error(log_color + 'Could not open port %s' % port + Style.RESET_ALL)


def thread_function(device):
    log_color = device.get('log_color')
    logging.info("Thread %s: starting", device.get('device_name'))
    open_serial_port(device)
    logging.info("Thread %s: finishing", device.get('device_name'))


def main():
    format = "%(asctime)s %(threadName)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%Y%m%dT%H%M%S")

    threads = list()
    for index, device in enumerate(DEVICES):
        logging.info("Main    : create and start thread %d.", index)
        t = threading.Thread(target=thread_function, args=(device, ))
        t.name = device.get('short_name')
        t.daemon = True
        threads.append(t)
        t.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)


if __name__ == "__main__":
    main()
