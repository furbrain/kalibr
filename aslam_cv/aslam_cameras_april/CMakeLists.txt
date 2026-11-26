kalibr_add_library(aslam_cameras_april
  SOURCES src/GridCalibrationTargetAprilgrid.cpp
  DEPS aslam_cameras ethz_apriltag2 sm_common sm_logging sm_boost sm_eigen
       ${OpenCV_LIBS} Boost::serialization Boost::system)

kalibr_add_python_module(aslam_cameras_april_python
  PACKAGE aslam_cameras_april
  SOURCES src/module.cpp
  DEPS aslam_cameras_april sm_python_headers)
kalibr_install_python_package(aslam_cameras_april python/aslam_cameras_april)
