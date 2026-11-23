kalibr_add_python_module(aslam_cv_backend_python
  PACKAGE aslam_cv_backend
  SOURCES
    src/module.cpp
    src/GridCalibration.cpp
  DEPS sm_common sm_python_headers sm_opencv sparse_block_matrix aslam_backend
       aslam_backend_expressions aslam_backend_python_headers aslam_cameras
       aslam_cv_error_terms aslam_splines aslam_cv_python_headers aslam_cv_backend
       aslam_time)
kalibr_install_python_package(aslam_cv_backend python/aslam_cv_backend)
