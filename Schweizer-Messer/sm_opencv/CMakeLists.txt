# Header-only.
kalibr_add_library(sm_opencv DEPS sm_common ${OpenCV_LIBS})
target_include_directories(sm_opencv INTERFACE ${OpenCV_INCLUDE_DIRS})
