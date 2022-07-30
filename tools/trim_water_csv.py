"""Tool to read a CSV from a zipped file and output selected fields."""

import csv
import errno
import logging
import io
from zipfile import ZipFile

from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('input', '', 'Path to zip file that contains the CSVs.')
flags.DEFINE_string('output', '', 'Path to output CSV file')

# The columns to export to the output CSV file.
# In this dictionary, the key corrsponds to the column name, and the value is
# the column index that it appears in the original CSV file.
# NOTE: The order of the data parameters in the .csv matters to be an acceptable
# file for our software (to support the performance of the multibeam depth
# sounder).
COLUMN_MAP = {
    'Speed of sound': 10,
    'Temperature': 2,
    'Salinity': 9,
    'Conductivity': 1,
    'Density anomaly': 13,
    'Pressure': 3,
}


def main(argv):
  """Main."""
  del argv  # Unused.

  zip_file = FLAGS.input
  output_filename = FLAGS.output

  selected_file = None
  with ZipFile(zip_file) as archive:
    logging.info('List of files in %s', zip_file)
    for file_name in archive.namelist():
      logging.info('File: %s', file_name)
      if file_name.endswith('_data.txt'):
        selected_file = file_name

    # Raise an exception if we can't find the file we are looking for in the zip.
    if not selected_file:
      raise FileNotFoundError(
          errno.ENOENT,
          f'Could not find a file that ends in \'_data.txt\' inside {zip_file}.')

    logging.info('Found input data file: %s', selected_file)

    with archive.open(selected_file, 'r') as data_file:
      with io.TextIOWrapper(data_file, encoding='utf-8') as text_file:
        reader = csv.reader(text_file)
        with open(output_filename, 'w', encoding='utf-8', newline='') as output:
          writer = csv.writer(output)
          row_index = 0
          for row in reader:
            modified_row = [
              row[COLUMN_MAP['Speed of sound']],
              row[COLUMN_MAP['Temperature']],
              row[COLUMN_MAP['Salinity']],
              row[COLUMN_MAP['Conductivity']],
              row[COLUMN_MAP['Density anomaly']],
              row[COLUMN_MAP['Pressure']],
              ]
            # Other than the first row, which contains the names of each column,
            # we need to convert all the values to floats.
            if row_index > 0:
              modified_row = [float(value) for value in modified_row]
            writer.writerow(modified_row)
            row_index += 1
    logging.info('Success!')
    logging.info('Written %i lines to %s.', row_index, output_filename)

if __name__ == "__main__":
  app.run(main)
