kalibr_add_library(sm_property_tree
  SOURCES
    src/PropertyTree.cpp
    src/BoostPropertyTreeImplementation.cpp
    src/BoostPropertyTree.cpp
    src/PropertyTreeImplementation.cpp
    src/BoostPropertyTreeSupport.cpp
  DEPS sm_common Boost::system Boost::filesystem Threads::Threads
  OPTIONS -D__STRICT_ANSI__)

kalibr_add_gtest(sm_property_tree-test
  SOURCES test/test_main.cpp test/BoostPropertyTreeImplementation.cpp
  DEPS sm_property_tree)
