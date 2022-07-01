"""Utilities related to UTC timestamps."""

import datetime

def get_utc_timestamp():
  """Get the current UTC time formatted."""
  return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')

def get_utc_timestamp_with_microseconds():
  """Get the current UTC time formatted, including microseconds."""
  return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')
