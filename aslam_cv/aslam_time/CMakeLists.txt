kalibr_add_library(aslam_time
  SOURCES src/time.cpp src/duration.cpp
  DEPS Boost::system rt)
