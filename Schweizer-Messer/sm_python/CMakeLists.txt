kalibr_add_python_module(sm_python
  PACKAGE sm
  SOURCES
    src/module.cpp
    src/export_rotational_kinematics.cpp
    src/export_rotations.cpp
    src/export_transformations.cpp
    src/export_quaternion_algebra.cpp
    src/export_homogeneous.cpp
    src/exportTransformation.cpp
    src/exportHomogeneousPoint.cpp
    src/exportTimestampCorrector.cpp
    src/exportPropertyTree.cpp
    src/exportEigen.cpp
    src/exportUncertainVector.cpp
    src/exportMatrixArchive.cpp
    src/export_kinematics_property_tree.cpp
    src/export_eigen_property_tree.cpp
    src/Logging.cpp
    src/exportNsecTime.cpp
    src/random.cpp
  DEPS sm_common sm_kinematics sm_timing sm_logging sm_matrix_archive
       sm_property_tree Boost::system Boost::serialization
  OPTIONS -D__STRICT_ANSI__)
kalibr_install_python_package(sm python/sm)
