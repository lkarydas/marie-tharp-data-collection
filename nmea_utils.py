"""NMEA utils."""

def get_message_code(sentence):
  """Get the message code from a NMEA sentence."""
  if len(sentence) > 5:
    return sentence[3:6]
  return None
