"""Reads data from a file and writes it to a serial port.."""

import itertools
import time

from absl import app
from absl import flags

import serial

FLAGS = flags.FLAGS

flags.DEFINE_string('port', 'COM2', 'Serial port name.')


def main(argv):
  del argv  # Unused.

  lines = []
  with open('./test_data/20220701T014728_maretron_nmea_gateway.dat', 'rb') as f:
    for line in f:
      lines.append(line[str(line).find(',')-1:])

  with serial.Serial(FLAGS.port, 4800, timeout=1) as ser:
    for line in itertools.cycle(lines):
      ser.write(line)
      time.sleep(0.1)


if __name__ == "__main__":
  app.run(main)
