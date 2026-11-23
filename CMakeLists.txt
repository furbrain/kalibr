cmake_minimum_required(VERSION 3.16)
project(kalibr VERSION 1.0.0 LANGUAGES C CXX)

# ROS-independent build of the Kalibr offline calibration tools.
#
#   cmake -S . -B build && cmake --build build -j
#   cmake --install build --prefix <prefix>
#
# or simply `pip install .` (see pyproject.toml).

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
list(APPEND CMAKE_MODULE_PATH
  ${CMAKE_CURRENT_SOURCE_DIR}/cmake
  ${CMAKE_CURRENT_SOURCE_DIR}/aslam_optimizer/sparse_block_matrix/cmake)

option(KALIBR_BUILD_TESTS "Build the C++ unit tests (needs GoogleTest)" OFF)

#############################################################################
# Install layout
#############################################################################
include(GNUInstallDirs)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module NumPy)

if(SKBUILD)
  # Building a wheel with scikit-build-core: everything goes to site-packages.
  set(_py_dir_default "${SKBUILD_PLATLIB_DIR}")
  set(_bin_dir_default "${SKBUILD_SCRIPTS_DIR}")
else()
  set(_py_dir_default
    "${CMAKE_INSTALL_LIBDIR}/python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}/site-packages")
  set(_bin_dir_default "${CMAKE_INSTALL_BINDIR}")
endif()
set(KALIBR_PYTHON_INSTALL_DIR "${_py_dir_default}" CACHE PATH "Where the Python packages are installed")
set(KALIBR_BIN_INSTALL_DIR "${_bin_dir_default}" CACHE PATH "Where the kalibr_* scripts are installed")
set(KALIBR_LIB_INSTALL_DIR "${KALIBR_PYTHON_INSTALL_DIR}/kalibr_libs" CACHE PATH
  "Where the Kalibr C++ shared libraries are installed")
# Python packages and extension modules are also assembled here, so the build
# can be used directly with PYTHONPATH=<build>/python.
set(KALIBR_PYTHON_BUILD_DIR "${CMAKE_BINARY_DIR}/python")

#############################################################################
# Third party dependencies
#############################################################################
find_package(Boost REQUIRED COMPONENTS
  system serialization thread filesystem regex
  python${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR})
add_library(kalibr_boost_python INTERFACE)
target_link_libraries(kalibr_boost_python INTERFACE
  Boost::python${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR})

find_package(Eigen3 REQUIRED NO_MODULE)
find_package(OpenCV REQUIRED)
find_package(SuiteSparse REQUIRED)
find_package(Threads REQUIRED)

if(KALIBR_BUILD_TESTS)
  find_package(GTest REQUIRED)
  enable_testing()
endif()

include(KalibrHelpers)

#############################################################################
# Packages, in dependency order
#############################################################################
set(_packages
  Schweizer-Messer/sm_common
  Schweizer-Messer/sm_random
  Schweizer-Messer/sm_boost
  Schweizer-Messer/sm_eigen
  Schweizer-Messer/sm_kinematics
  Schweizer-Messer/sm_timing
  Schweizer-Messer/sm_logging
  Schweizer-Messer/sm_property_tree
  Schweizer-Messer/sm_matrix_archive
  Schweizer-Messer/sm_opencv
  Schweizer-Messer/numpy_eigen
  Schweizer-Messer/sm_python

  aslam_optimizer/sparse_block_matrix
  aslam_optimizer/aslam_backend
  aslam_optimizer/aslam_backend_expressions
  aslam_optimizer/aslam_backend_python

  aslam_nonparametric_estimation/bsplines
  aslam_nonparametric_estimation/bsplines_python
  aslam_nonparametric_estimation/aslam_splines
  aslam_nonparametric_estimation/aslam_splines_python

  aslam_cv/aslam_time
  aslam_cv/aslam_cameras
  aslam_cv/aslam_imgproc
  aslam_cv/aslam_cv_serialization
  aslam_cv/aslam_cv_python
  aslam_cv/aslam_cv_backend
  aslam_cv/aslam_cv_error_terms
  aslam_cv/aslam_cv_backend_python

  aslam_offline_calibration/ethz_apriltag2
  aslam_cv/aslam_cameras_april

  aslam_incremental_calibration/incremental_calibration
  aslam_incremental_calibration/incremental_calibration_python

  aslam_offline_calibration/kalibr
)
foreach(_pkg ${_packages})
  add_subdirectory(${_pkg})
endforeach()
