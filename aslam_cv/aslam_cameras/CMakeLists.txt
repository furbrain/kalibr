kalibr_add_library(aslam_cameras
  SOURCES
    src/CameraGeometryBase.cpp
    src/GlobalShutter.cpp
    src/RollingShutter.cpp
    src/NoMask.cpp
    src/NoDistortion.cpp
    src/RadialTangentialDistortion.cpp
    src/EquidistantDistortion.cpp
    src/FovDistortion.cpp
    src/ImageMask.cpp
    src/GridCalibrationTargetObservation.cpp
    src/GridCalibrationTargetBase.cpp
    src/GridCalibrationTargetCheckerboard.cpp
    src/GridCalibrationTargetCirclegrid.cpp
    src/GridDetector.cpp
    src/Triangulation.cpp
    src/FrameBase.cpp
    src/KeypointBase.cpp
    src/DescriptorBase.cpp
    src/BackProjection.cpp
    src/Landmark.cpp
    src/Image.cpp
  DEPS sm_common sm_eigen sm_boost sm_kinematics sm_logging aslam_time sm_opencv
       sm_property_tree sm_random ${OpenCV_LIBS}
       Boost::system Boost::serialization Boost::filesystem
  OPTIONS -Wno-deprecated-copy)

kalibr_add_gtest(aslam_cameras_tests
  SOURCES
    test/test_main.cpp
    test/PinholeCameraGeometry.cpp
    test/OmniCameraGeometry.cpp
    test/ExtendedUnifiedCameraGeometry.cpp
    test/DoubleSphereCameraGeometry.cpp
    test/RadialTangentialDistortion.cpp
    test/EquidistantDistortion.cpp
    test/FovDistortion.cpp
    test/Triangulation.cpp
    test/testFrame.cpp
    test/GridCalibration.cpp
  DEPS aslam_cameras
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/test)
if(KALIBR_BUILD_TESTS)
  # The tests read these images and write serialization files next to them.
  foreach(_img testImageCheckerboard.jpg testImageCircleGrid.jpg)
    configure_file(test/${_img} ${CMAKE_CURRENT_BINARY_DIR}/test/${_img} COPYONLY)
  endforeach()
endif()
