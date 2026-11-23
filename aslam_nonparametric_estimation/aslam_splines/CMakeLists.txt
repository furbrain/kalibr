kalibr_add_library(aslam_splines
  SOURCES
    src/BSplinePoseDesignVariable.cpp
    src/BSplineExpressions.cpp
    src/EuclideanBSplineDesignVariable.cpp
  DEPS aslam_backend aslam_backend_expressions bsplines sparse_block_matrix
       sm_common sm_kinematics sm_timing Boost::system)

kalibr_add_gtest(aslam_splines_test
  SOURCES
    test/test_main.cpp
    test/TestBSplineExpressions.cpp
    test/TestErrors.cpp
  DEPS aslam_splines)
