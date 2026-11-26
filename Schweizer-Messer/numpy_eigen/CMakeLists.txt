# Headers used by every Boost.Python module for numpy <-> Eigen conversion.
add_library(numpy_eigen_headers INTERFACE)
target_include_directories(numpy_eigen_headers INTERFACE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/include/numpy_eigen)
target_link_libraries(numpy_eigen_headers INTERFACE Eigen3::Eigen)

include(src/autogen_files.cmake)
kalibr_add_python_module(numpy_eigen
  PACKAGE numpy_eigen
  SOURCES ${AUTOGEN_FILES}
  DEPS Boost::system
  OPTIONS -D__STRICT_ANSI__ -fpermissive)
kalibr_install_python_package(numpy_eigen src/numpy_eigen)
