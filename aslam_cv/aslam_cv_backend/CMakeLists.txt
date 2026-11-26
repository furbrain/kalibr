kalibr_add_library(aslam_cv_backend
  SOURCES src/GridCalibrationTargetDesignVariableContainer.cpp
  DEPS sm_common sm_boost sm_kinematics sm_eigen sm_opencv sm_property_tree
       sm_logging sm_timing aslam_backend aslam_backend_expressions aslam_time
       aslam_cameras sparse_block_matrix Boost::system)

kalibr_add_gtest(aslam_cv_backend_test
  SOURCES test/test_main.cpp
  DEPS aslam_cv_backend)
