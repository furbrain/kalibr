kalibr_add_library(bsplines
  SOURCES src/BSpline.cpp src/BSplinePose.cpp
  DEPS sm_common sm_timing sm_eigen sm_kinematics sparse_block_matrix)
