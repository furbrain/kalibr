kalibr_add_python_module(aslam_backend_python
  PACKAGE aslam_backend
  SOURCES
    src/module.cpp
    src/Backend.cpp
    src/Optimizer.cpp
    src/OptimizerOptions.cpp
    src/OptimizationProblem.cpp
    src/DesignVariable.cpp
    src/ErrorTerm.cpp
    src/MEstimators.cpp
    src/JacobianContainer.cpp
    src/BackendExpressions.cpp
    src/CompressedColumnMatrix.cpp
    src/LinearSystemSolver.cpp
    src/ErrorTermTransformation.cpp
    src/TrustRegionPolicies.cpp
    src/SparseBlockMatrix.cpp
  DEPS aslam_backend aslam_backend_expressions sparse_block_matrix sm_common
       sm_kinematics sm_timing Boost::thread
  OPTIONS -Wextra -Winit-self -Woverloaded-virtual -Wnon-virtual-dtor -Wsign-promo -Wno-long-long)
kalibr_install_python_package(aslam_backend python/aslam_backend)
