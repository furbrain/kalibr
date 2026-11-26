#############################################################################
# Error terms (C++ library + Python bindings)
#############################################################################
kalibr_add_library(kalibr_errorterms
  SOURCES
    src/EuclideanError.cpp
    src/GyroscopeError.cpp
    src/AccelerometerError.cpp
  DEPS aslam_backend aslam_backend_expressions sparse_block_matrix sm_common
       sm_kinematics)

kalibr_add_python_module(kalibr_errorterms_python
  PACKAGE kalibr_errorterms
  SOURCES src/module.cpp
  DEPS kalibr_errorterms aslam_backend_python_headers)

kalibr_add_gtest(kalibr_test
  SOURCES test/test_main.cpp test/TestErrorTerms.cpp
  DEPS kalibr_errorterms)

#############################################################################
# Python packages
#############################################################################
foreach(_pkg
    kalibr_common
    kalibr_errorterms
    kalibr_camera_calibration
    kalibr_imu_camera_calibration
    kalibr_rs_camera_calibration)
  kalibr_install_python_package(${_pkg} python/${_pkg})
endforeach()

#############################################################################
# Command line tools
#############################################################################
set(KALIBR_SCRIPTS
  kalibr_calibrate_cameras
  kalibr_calibrate_imu_camera
  kalibr_calibrate_rs_cameras
  kalibr_visualize_calibration
  kalibr_visualize_distortion
  kalibr_create_target_pdf
  kalibr_bagcreater
  kalibr_bagextractor
)
foreach(_script ${KALIBR_SCRIPTS})
  install(PROGRAMS python/${_script} DESTINATION ${KALIBR_BIN_INSTALL_DIR})
  configure_file(python/${_script} ${CMAKE_BINARY_DIR}/bin/${_script} COPYONLY)
endforeach()
