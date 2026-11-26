"""ROS-independent access to the messages of one topic in a ROS 1 or ROS 2 bag.

Uses the pure Python `rosbags` library, so no ROS installation is needed.
Supported inputs:
  * ROS 1 bags (``*.bag``)
  * ROS 2 bags: the bag directory (containing ``metadata.yaml``), or a single
    ``*.db3`` / ``*.mcap`` file inside such a directory.
"""
import os
from pathlib import Path

import cv2
import numpy as np

from rosbags.highlevel import AnyReader
from rosbags.interfaces import MessageDefinitionFormat
from rosbags.rosbag2 import Reader as Rosbag2Reader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg


def _resolvePath(bagfile):
    path = Path(bagfile).expanduser()
    if not path.exists():
        raise RuntimeError("Bag {0} does not exist.".format(bagfile))
    # A storage file of a ROS 2 bag: open the bag directory it belongs to.
    if path.is_file() and path.suffix in ('.db3', '.mcap') and (path.parent / 'metadata.yaml').exists():
        return path.parent
    return path


class _Rosbag2DirReader(object):
    """ROS 2 bag directory reader with the subset of the AnyReader interface used here.

    AnyReader picks the bag format from the file suffix, so a ROS 2 bag
    directory named e.g. "ros2.bag" would be opened as a ROS 1 bag.
    """

    def __init__(self, path):
        self._reader = Rosbag2Reader(path)
        self.typestore = get_typestore(Stores.ROS2_HUMBLE)

    def open(self):
        self._reader.open()
        self.connections = self._reader.connections
        # Register message types the bag defines but the typestore lacks.
        types = {}
        for connection in self.connections:
            if (connection.msgtype not in self.typestore.types
                    and connection.msgdef.format == MessageDefinitionFormat.MSG):
                types.update(get_types_from_msg(connection.msgdef.data, connection.msgtype))
        if types:
            self.typestore.register(types)

    def messages(self, connections=()):
        return self._reader.messages(connections=connections)

    def deserialize(self, rawdata, msgtype):
        return self.typestore.deserialize_cdr(rawdata, msgtype)

    def close(self):
        self._reader.close()


def _openBag(bagfile):
    path = _resolvePath(bagfile)
    if path.is_dir():
        # ROS 2 bags are directories (metadata.yaml + storage files).
        return _Rosbag2DirReader(path)
    # ROS 1 bags are single files.
    return AnyReader([path])


def stampToNsec(stamp):
    """builtin_interfaces/Time (ROS 2) or the equivalent ROS 1 time -> int ns."""
    return int(stamp.sec) * 1000000000 + int(stamp.nanosec)


class BagTopicReader(object):
    """Loads all messages of one topic of a bag.

    The serialized messages of the topic are kept in memory, so messages can be
    accessed by index in any order (the readers sort by header timestamp and
    may shuffle). Messages are only deserialized when requested.
    """

    def __init__(self, bagfile, topic):
        self.bagfile = bagfile
        self.topic = topic
        if topic is None:
            raise RuntimeError("Please pass in a topic name for bag {0}".format(bagfile))

        self._reader = _openBag(bagfile)
        self._reader.open()
        try:
            connections = [c for c in self._reader.connections if c.topic == topic]
            if not connections:
                available = sorted(set(c.topic for c in self._reader.connections))
                raise RuntimeError("Could not find topic {0} in {1}.\nAvailable topics: {2}".format(
                    topic, bagfile, ", ".join(available)))
            self.msgtype = connections[0].msgtype

            self._connections = []
            self._rawdata = []
            self.bag_stamps = []  # receive time recorded in the bag [ns]
            for connection, timestamp, rawdata in self._reader.messages(connections=connections):
                self._connections.append(connection)
                self._rawdata.append(rawdata)
                self.bag_stamps.append(timestamp)
        except Exception:
            self._reader.close()
            raise
        # Header stamps of all messages [ns]
        self.header_stamps = [stampToNsec(self.deserialize(i).header.stamp) for i in range(len(self))]

    def __len__(self):
        return len(self._rawdata)

    def deserialize(self, idx):
        connection = self._connections[idx]
        return self._reader.deserialize(self._rawdata[idx], connection.msgtype)

    def close(self):
        self._reader.close()


#############################################################################
# Image decoding (replaces cv_bridge)
#############################################################################

def _imageArray(msg, dtype, channels):
    dtype = np.dtype(dtype)
    if dtype.itemsize > 1:
        dtype = dtype.newbyteorder('>' if msg.is_bigendian else '<')
    row_elems = msg.step // dtype.itemsize
    data = np.frombuffer(bytes(msg.data), dtype=dtype, count=msg.height * row_elems)
    img = data.reshape(msg.height, row_elems)[:, :msg.width * channels]
    if channels > 1:
        img = img.reshape(msg.height, msg.width, channels)
    return np.array(img, dtype=dtype.newbyteorder('='))


_RAW_DECODERS = {
    # encoding: (dtype, channels, cv2 conversion to gray or None)
    '16UC1': ('u2', 1, None),
    'mono16': ('u2', 1, None),
    '8UC1': ('u1', 1, None),
    'mono8': ('u1', 1, None),
    '8UC3': ('u1', 3, cv2.COLOR_BGR2GRAY),
    'bgr8': ('u1', 3, cv2.COLOR_BGR2GRAY),
    'rgb8': ('u1', 3, cv2.COLOR_RGB2GRAY),
    '8UC4': ('u1', 4, cv2.COLOR_BGRA2GRAY),
    'bgra8': ('u1', 4, cv2.COLOR_BGRA2GRAY),
    'rgba8': ('u1', 4, cv2.COLOR_RGBA2GRAY),
    # bayer conversions from
    # https://github.com/ros-perception/image_pipeline/blob/6caf51bd4484ae846cd8a199f7a6a4b060c6373a/image_proc/src/libimage_proc/processor.cpp#L70
    'bayer_rggb8': ('u1', 1, cv2.COLOR_BAYER_BG2GRAY),
    'bayer_bggr8': ('u1', 1, cv2.COLOR_BAYER_RG2GRAY),
    'bayer_gbrg8': ('u1', 1, cv2.COLOR_BAYER_GR2GRAY),
    'bayer_grbg8': ('u1', 1, cv2.COLOR_BAYER_GB2GRAY),
}


def decodeImageMsg(msg, msgtype, uncompress=None):
    """Convert an image message into an 8 bit grayscale numpy array."""
    if msgtype.endswith('ImageSnappyMsg'):
        if uncompress is None:
            from snappy import uncompress
        return np.reshape(np.frombuffer(uncompress(bytes(msg.data)), dtype='uint8'),
                          (msg.height, msg.width), order="C").copy()

    if msgtype == 'sensor_msgs/msg/CompressedImage':
        # compressed images only have either mono or BGR normally (png and jpeg)
        img = cv2.imdecode(np.frombuffer(bytes(msg.data), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None:
            raise RuntimeError("Could not decode compressed image (format '{0}')".format(msg.format))
        if img.ndim > 2 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.ndim > 2 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return img

    if msgtype == 'sensor_msgs/msg/Image':
        if msg.encoding not in _RAW_DECODERS:
            raise RuntimeError(
                "Unsupported Image Encoding: '{}'\nSupported are: {}".format(
                    msg.encoding, ", ".join(sorted(_RAW_DECODERS))))
        dtype, channels, conversion = _RAW_DECODERS[msg.encoding]
        img = _imageArray(msg, dtype, channels)
        if dtype == 'u2':
            img = (img / 256).astype("uint8")
        if conversion is not None:
            img = cv2.cvtColor(img, conversion)
        return img

    raise RuntimeError(
        "Unsupported Image Type: '{}'\nSupported are: "
        "mv_cameras/ImageSnappyMsg, sensor_msgs/CompressedImage, sensor_msgs/Image".format(msgtype))
