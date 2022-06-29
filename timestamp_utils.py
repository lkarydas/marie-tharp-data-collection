"""Utilities related to UTC timestamps."""

import datetime

def get_utc_timestamp():
  """Get the current UTC time formatted."""
  return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
