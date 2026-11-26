kalibr_add_library(sm_common
  SOURCES src/progress_info.cpp
  DEPS Boost::system
  OPTIONS -Wall -D__STRICT_ANSI__ -Wno-deprecated-copy)

kalibr_add_gtest(sm_common-test
  SOURCES
    test/test_main.cpp
    test/maths.cpp
    test/serialization_macros.cpp
    test/numerical_comparisons.cpp
    test/hash_id.cpp
  DEPS sm_common)
