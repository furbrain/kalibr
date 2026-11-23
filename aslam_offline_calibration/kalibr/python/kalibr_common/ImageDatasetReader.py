import numpy as np
import aslam_cv as acv
import sm

from .BagReader import BagTopicReader, decodeImageMsg


class BagImageDatasetReaderIterator(object):
  def __init__(self, dataset, indices=None):
    self.dataset = dataset
    if indices is None:
      self.indices = np.arange(dataset.numImages())
    else:
      self.indices = indices
    self.iter = self.indices.__iter__()

  def __iter__(self):
    return self

  def __next__(self):
    idx = next(self.iter)
    return self.dataset.getImage(idx)

  next = __next__


class BagImageDatasetReader(object):
  """Reads the images of one topic of a ROS 1 or ROS 2 bag (no ROS needed)."""

  def __init__(self, bagfile, imagetopic, bag_from_to=None, perform_synchronization=False, bag_freq=None):
    self.bagfile = bagfile
    self.topic = imagetopic
    self.perform_synchronization = perform_synchronization
    self.uncompress = None
    if imagetopic is None:
      raise RuntimeError(
          "Please pass in a topic name referring to the image stream in the bag file\n{0}".format(bagfile))

    self.bag = BagTopicReader(bagfile, imagetopic)
    # one entry per message of the topic, kept for compatibility
    self.index = list(range(len(self.bag)))
    if len(self.index) == 0:
      raise RuntimeError("Could not find topic {0} in {1}.".format(imagetopic, self.bagfile))

    self.indices = np.arange(len(self.index))

    # sort the indices by header.stamp
    self.indices = self.sortByTime(self.indices)

    # remove the indices outside the timespan [bag_start_time, bag_end_time]
    if bag_from_to:
      self.indices = self.truncateIndicesFromTime(self.indices, bag_from_to)

    # remove indices not at the correct frequency
    if bag_freq:
      self.indices = self.truncateIndicesFromFreq(self.indices, bag_freq)

  def _headerSec(self, idx):
    return self.bag.header_stamps[idx] / 1.0e9

  # sort the messages by the header time not message time
  def sortByTime(self, indices):
    self.timestamp_corrector = sm.DoubleTimestampCorrector()
    timestamps = list()
    for idx in indices:
      timestamps.append(self.bag.header_stamps[idx])
      if self.perform_synchronization:
        self.timestamp_corrector.correctTimestamp(self._headerSec(idx),
                                                  self.bag.bag_stamps[idx] / 1.0e9)

    sorted_tuples = sorted(zip(timestamps, indices))
    sorted_indices = [tuple_value[1] for tuple_value in sorted_tuples]
    return sorted_indices

  def truncateIndicesFromTime(self, indices, bag_from_to):
    timestamps = [self._headerSec(idx) for idx in indices]

    bagstart = min(timestamps)
    baglength = max(timestamps) - bagstart

    # some value checking
    if bag_from_to[0] >= bag_from_to[1]:
      raise RuntimeError("Bag start time must be bigger than end time.".format(bag_from_to[0]))
    if bag_from_to[0] < 0.0:
      sm.logWarn("Bag start time of {0} s is smaller 0".format(bag_from_to[0]))
    if bag_from_to[1] > baglength:
      sm.logWarn("Bag end time of {0} s is bigger than the total length of {1} s".format(
          bag_from_to[1], baglength))

    # find the valid timestamps
    valid_indices = []
    for idx, timestamp in zip(indices, timestamps):
      if timestamp >= (bagstart + bag_from_to[0]) and timestamp <= (bagstart + bag_from_to[1]):
        valid_indices.append(idx)
    sm.logWarn(
        "BagImageDatasetReader: truncated {0} / {1} images (from-to).".format(len(indices) - len(valid_indices), len(indices)))
    return valid_indices

  def truncateIndicesFromFreq(self, indices, freq):

    # some value checking
    if freq < 0.0:
      raise RuntimeError("Frequency {0} Hz is smaller 0".format(freq))

    # find the valid timestamps
    timestamp_last = -1
    valid_indices = []
    for idx in indices:
      timestamp = self._headerSec(idx)
      if timestamp_last < 0.0:
        timestamp_last = timestamp
        valid_indices.append(idx)
        continue
      if (timestamp - timestamp_last) >= 1.0 / freq:
        timestamp_last = timestamp
        valid_indices.append(idx)
    sm.logWarn(
      "BagImageDatasetReader: truncated {0} / {1} images (frequency)".format(len(indices) - len(valid_indices), len(indices)))
    return valid_indices

  def __iter__(self):
    # Reset the bag reading
    return self.readDataset()

  def readDataset(self):
    return BagImageDatasetReaderIterator(self, self.indices)

  def readDatasetShuffle(self):
    indices = self.indices
    np.random.shuffle(indices)
    return BagImageDatasetReaderIterator(self, indices)

  def numImages(self):
    return len(self.indices)

  def getImage(self, idx):
    stamp_ns = self.bag.header_stamps[idx]
    if self.perform_synchronization:
      timestamp = acv.Time(self.timestamp_corrector.getLocalTime(stamp_ns / 1.0e9))
    else:
      timestamp = acv.Time(stamp_ns // 1000000000, stamp_ns % 1000000000)
    msg = self.bag.deserialize(idx)
    if self.uncompress is None and self.bag.msgtype.endswith('ImageSnappyMsg'):
      from snappy import uncompress
      self.uncompress = uncompress
    img_data = decodeImageMsg(msg, self.bag.msgtype, self.uncompress)
    return (timestamp, img_data)
