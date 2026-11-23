kalibr_add_library(sm_kinematics
  SOURCES
    src/quaternion_algebra.cpp
    src/rotations.cpp
    src/transformations.cpp
    src/RotationalKinematics.cpp
    src/RotationVector.cpp
    src/EulerAnglesZYX.cpp
    src/EulerAnglesYawPitchRoll.cpp
    src/EulerRodriguez.cpp
    src/Transformation.cpp
    src/homogeneous_coordinates.cpp
    src/HomogeneousPoint.cpp
    src/UncertainTransformation.cpp
    src/UncertainHomogeneousPoint.cpp
    src/three_point_methods.cpp
    src/EulerAnglesZXY.cpp
  DEPS sm_common sm_eigen sm_boost sm_random
       Boost::system Boost::serialization Boost::filesystem
  OPTIONS -Wall)

kalibr_add_gtest(sm_kinematics-test
  SOURCES
    test/RotationalKinematicsTests.cpp
    test/QuaternionTests.cpp
    test/TransformationTests.cpp
    test/transformations.cpp
    test/HomogeneousPoint.cpp
    test/UncertainHomogeneousPoint.cpp
    test/test_main.cpp
    test/UncertainTransformationTests.cpp
    test/homogeneous_coordinates.cpp
    test/three_point_methods.cpp
  DEPS sm_kinematics)
