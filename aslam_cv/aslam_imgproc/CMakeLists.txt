kalibr_add_library(aslam_imgproc
  SOURCES src/UndistorterBase.cpp
  DEPS aslam_cameras aslam_time sm_common sm_eigen sm_random sm_boost sm_kinematics
       sm_opencv sm_logging sm_property_tree Boost::system
  OPTIONS -Wno-deprecated-copy -Wno-maybe-uninitialized)
