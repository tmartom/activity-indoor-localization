from errlog import log_error


class FeedProcessor(object):
  """Processes a classifier feed data file to provide easy updates.
  """

  def __init__(self, feed_file_name, loop_feed=True):
    """Reads the given filename and tries to parse the classifier feed.
    
    Args:
      feed_file_name: the name of the file that contains all probabilities for
          each of the activities. Empty lines or lines starting with '#' will be
          ignored. All other lines should have a series of space-delimited
          probability values, one for each region class, in the same order as
          defined in the BuildingMap class. A line can also start with a '+', in
          which case the turn angle for the step associated with the
          probabilities of the line above it will be updated.
      loop_feed: (optional) set to False if this feed shouldn't loop around.
          Otherwise, when the data stream runs out, it will loop from the
          beginning.
    
    Returns:
      A 2D list floats that contains the probabilities for each region for every
      iteration interval (frame). These probabilities are intended to be given
      one at a time to the BuildingMap object to update its region probabilites.
    """
    self._probability_list = []
    self._turn_angles = []
    self._loop_feed = loop_feed
    try:
      f = open(feed_file_name, 'r')
      for line in f:
        line = line.strip()
        if len(line) == 0 or line.startswith('#'):
          continue
        # If line begins with a '+', that means it's a turn angle, so add that
        # turn value to the previous position.
        if line.startswith('+'):
          line = line[1:]
          line = line.strip()
          turn_angle = float(line)
          if len(self._turn_angles) > 0:
            self._turn_angles[-1] = turn_angle
        # Otherwise add the probabilities and a turn angle of 0.
        else:
          line = line.split()
          self._probability_list.append(map(float, line))
          self._turn_angles.append(0)
    except:
      log_error('failed to load feed file: {}'.format(feed_file_name))
    self._next_index = 0
    self._num_feeds = len(self._probability_list)

  def has_next(self):
    """Returns True if there is an available feed in the stream.

    Returns:
      True if there is another entree in the feed, False otherwise. If looping
      is enabled, this should always return True if there is at least one feed
      entry.
    """
    return self._num_feeds > self._next_index

  def get_next(self):
    """Returns the next feed probabilities and turn angle.

    Use has_next() to ensure that this returns a valid list of probabilities.

    Returns:
      A tuple (probabilities, turn_angle) where the probabilities is a list of
      the map region probabilities for the next iteration, and turn_angle is
      the angle by which the user is supposedly turning for the next iteration.
      If there is no more data in the stream and looping is turned off, probs
      will be None and turn_angle will be 0.
    """
    probs = None
    turn_angle = 0
    if self._num_feeds > self._next_index:
      probs = self._probability_list[self._next_index]
      turn_angle = self._turn_angles[self._next_index]
      self._next_index += 1
      # If index is out of bounds, reset if we are looping the classifier feed.
      if self._next_index >= self._num_feeds and self._loop_feed:
        self._next_index = 0
    return probs, turn_angle