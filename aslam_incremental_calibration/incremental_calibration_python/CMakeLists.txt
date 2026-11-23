kalibr_add_python_module(incremental_calibration_python
  PACKAGE incremental_calibration
  SOURCES
    src/module.cpp
    src/OptimizationProblem.cpp
    src/IncrementalEstimator.cpp
    src/LinearSolver.cpp
  DEPS aslam_backend incremental_calibration sm_property_tree)
kalibr_install_python_package(incremental_calibration src/incremental_calibration)
