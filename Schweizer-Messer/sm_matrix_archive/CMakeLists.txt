kalibr_add_library(sm_matrix_archive
  SOURCES src/MatrixArchive.cpp
  DEPS sm_common Eigen3::Eigen Boost::system Boost::filesystem Threads::Threads
  OPTIONS -D__STRICT_ANSI__)

kalibr_add_gtest(sm_matrix_archive-test
  SOURCES test/test_main.cpp test/TestMatrixArchive.cpp
  DEPS sm_matrix_archive)
