kalibr_add_library(sm_boost
  SOURCES
    src/JobQueue.cpp
    src/portable_binary_iarchive.cpp
    src/portable_binary_oarchive.cpp
  DEPS sm_common Boost::system Boost::serialization Boost::thread)

kalibr_add_gtest(sm_boost-test
  SOURCES test/test_main.cpp test/testFuture.cpp
  DEPS sm_boost)
