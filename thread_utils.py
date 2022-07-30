"""Utility methods around threads."""

def are_all_threads_dead(threads):
  """Returns True if all the threads in the list are dead."""
  for thread in threads:
    if thread.is_alive():
      return False
  return True
