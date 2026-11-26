kalibr_add_library(sm_eigen
  SOURCES src/random.cpp
  DEPS sm_common sm_random Eigen3::Eigen Boost::system Boost::serialization)

kalibr_add_gtest(sm_eigen-test
  SOURCES
    test/test_main.cpp
    test/EigenSerializationTests.cpp
    test/MatrixSqrtTest.cpp
  DEPS sm_eigen)
