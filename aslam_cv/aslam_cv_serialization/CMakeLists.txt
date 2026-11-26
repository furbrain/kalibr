include(autogen_cameras.cmake)
kalibr_add_library(aslam_cv_serialization
  SOURCES
    ${AUTOGEN_CAMERA_CPP_FILES}
    src/FrameBaseSerialization.cpp
  DEPS aslam_cameras aslam_time sm_common sm_boost sm_property_tree sm_eigen
       sm_kinematics sm_opencv sm_logging sm_random
       Boost::serialization Boost::system)
