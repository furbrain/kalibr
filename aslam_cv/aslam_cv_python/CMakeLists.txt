kalibr_add_python_module(aslam_cv_python
  PACKAGE aslam_cv
  SOURCES
    src/module.cpp
    src/CameraGeometries.cpp
    src/CameraGeometry.cpp
    src/Time.cpp
    src/Frontend.cpp
    src/Frame.cpp
    src/CameraProjections.cpp
    src/CameraShutters.cpp
    src/GridCalibration.cpp
    src/Undistorters.cpp
    src/OmniUndistorter.cpp
    src/PinholeUndistorter.cpp
  DEPS sm_common sm_eigen sm_kinematics sm_python_headers sm_opencv
       aslam_cv_serialization aslam_imgproc aslam_cameras aslam_time
       Boost::serialization
  OPTIONS -Wextra -Winit-self -Woverloaded-virtual -Wnon-virtual-dtor -Wsign-promo
          -Wno-long-long -Wno-deprecated-copy)
kalibr_install_python_package(aslam_cv python/aslam_cv)
