kalibr_add_python_module(bsplines_python
  PACKAGE bsplines
  SOURCES
    src/SplinePython.cpp
    src/BSplinePython.cpp
    src/BSplinePosePython.cpp
  DEPS bsplines sparse_block_matrix sm_common sm_kinematics)
kalibr_install_python_package(bsplines python/bsplines)
