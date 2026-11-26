kalibr_add_library(sm_timing
  SOURCES src/Timer.cpp src/NsecTimeUtilities.cpp
  DEPS sm_common sm_random Boost::system
  OPTIONS -D__STRICT_ANSI__)

kalibr_add_gtest(sm_timing-test
  SOURCES
    test/test_main.cpp
    test/TestTimestampCorrector.cpp
    test/TestNsecTimeUtilities.cpp
  DEPS sm_timing)
