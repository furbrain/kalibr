kalibr_add_python_module(aslam_splines_python
  PACKAGE aslam_splines
  SOURCES
    src/spline_module.cpp
    src/BSplineMotionError.cpp
    src/SimpleSplineError.cpp
  DEPS aslam_splines bsplines aslam_backend aslam_backend_expressions
       aslam_backend_python_headers sparse_block_matrix sm_common sm_kinematics sm_timing
       aslam_cameras aslam_time sm_opencv sm_property_tree sm_logging)
kalibr_install_python_package(aslam_splines python/aslam_splines)
