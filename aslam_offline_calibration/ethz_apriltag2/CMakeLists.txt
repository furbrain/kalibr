file(GLOB _apriltag_sources CONFIGURE_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cc)
kalibr_add_library(ethz_apriltag2
  SOURCES ${_apriltag_sources}
  DEPS Eigen3::Eigen ${OpenCV_LIBS}
  OPTIONS -O3)
target_include_directories(ethz_apriltag2 PUBLIC ${OpenCV_INCLUDE_DIRS})
# The apriltags_demo example (src/example) needs a V4L2 camera and is not built.
