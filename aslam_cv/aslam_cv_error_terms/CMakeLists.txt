# Header-only.
kalibr_add_library(aslam_cv_error_terms
  DEPS sm_logging sm_property_tree sm_opencv sm_kinematics aslam_time aslam_cameras
       aslam_backend aslam_cv_backend aslam_backend_expressions sm_boost sm_eigen
       sm_timing sparse_block_matrix aslam_splines)
