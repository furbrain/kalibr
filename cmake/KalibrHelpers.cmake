# Helper functions for the ROS-independent Kalibr build.
#
# Every C++ library is built as a shared library and installed into
# ${KALIBR_LIB_INSTALL_DIR}. Every Boost.Python extension module is built as
# lib<target>.so (the name the Python packages import) and installed next to
# the Python sources of its package under ${KALIBR_PYTHON_INSTALL_DIR}.
# RPATHs are relative ($ORIGIN) so the installed tree can be relocated, which
# is also what makes a pip wheel work.

include_guard(GLOBAL)

# Compute an $ORIGIN-relative RPATH from a python install sub directory to the
# library install directory.
function(_kalibr_rpath_from out_var from_dir)
  file(RELATIVE_PATH _rel "/${from_dir}" "/${KALIBR_LIB_INSTALL_DIR}")
  if(_rel STREQUAL "")
    set(${out_var} "$ORIGIN" PARENT_SCOPE)
  else()
    set(${out_var} "$ORIGIN/${_rel}" PARENT_SCOPE)
  endif()
endfunction()

# kalibr_add_library(<name>
#   [SOURCES <src>...]          # omit for a header-only (INTERFACE) library
#   [DEPS <target>...]          # public link dependencies
#   [DEFINITIONS <def>...]      # public compile definitions
#   [OPTIONS <opt>...]          # private compile options
# )
# Headers are taken from ${CMAKE_CURRENT_SOURCE_DIR}/include.
function(kalibr_add_library name)
  cmake_parse_arguments(ARG "" "" "SOURCES;DEPS;DEFINITIONS;OPTIONS" ${ARGN})
  if(ARG_SOURCES)
    add_library(${name} SHARED ${ARG_SOURCES})
    target_include_directories(${name} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_link_libraries(${name} PUBLIC ${ARG_DEPS})
    if(ARG_DEFINITIONS)
      target_compile_definitions(${name} PUBLIC ${ARG_DEFINITIONS})
    endif()
    if(ARG_OPTIONS)
      target_compile_options(${name} PRIVATE ${ARG_OPTIONS})
    endif()
    set_target_properties(${name} PROPERTIES INSTALL_RPATH "$ORIGIN")
    install(TARGETS ${name}
      LIBRARY DESTINATION ${KALIBR_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${KALIBR_LIB_INSTALL_DIR}
      RUNTIME DESTINATION ${KALIBR_LIB_INSTALL_DIR})
  else()
    add_library(${name} INTERFACE)
    target_include_directories(${name} INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_link_libraries(${name} INTERFACE ${ARG_DEPS})
    if(ARG_DEFINITIONS)
      target_compile_definitions(${name} INTERFACE ${ARG_DEFINITIONS})
    endif()
  endif()
endfunction()

# kalibr_add_python_module(<target>
#   PACKAGE <python package name>  # where the module is installed; "." = top level
#   SOURCES <src>...
#   [DEPS <target>...]
#   [OPTIONS <opt>...]
# )
# Builds lib<target>.so. If ${CMAKE_CURRENT_SOURCE_DIR}/include exists, an
# INTERFACE target <target>_headers is created so other modules can use the
# exported headers.
function(kalibr_add_python_module target)
  cmake_parse_arguments(ARG "" "PACKAGE" "SOURCES;DEPS;OPTIONS" ${ARGN})
  add_library(${target} MODULE ${ARG_SOURCES})
  target_link_libraries(${target} PRIVATE
    ${ARG_DEPS} numpy_eigen_headers kalibr_boost_python Python3::Module Python3::NumPy)
  if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_include_directories(${target} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    if(NOT TARGET ${target}_headers)
      add_library(${target}_headers INTERFACE)
      target_include_directories(${target}_headers INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    endif()
  endif()
  if(ARG_OPTIONS)
    target_compile_options(${target} PRIVATE ${ARG_OPTIONS})
  endif()

  if(ARG_PACKAGE STREQUAL ".")
    set(_dest "${KALIBR_PYTHON_INSTALL_DIR}")
    set(_build_dir "${KALIBR_PYTHON_BUILD_DIR}")
  else()
    set(_dest "${KALIBR_PYTHON_INSTALL_DIR}/${ARG_PACKAGE}")
    set(_build_dir "${KALIBR_PYTHON_BUILD_DIR}/${ARG_PACKAGE}")
  endif()
  _kalibr_rpath_from(_rpath "${_dest}")
  # Keep the "lib" prefix and a plain ".so" suffix: the Python packages do
  # "from .lib<target> import *".
  set_target_properties(${target} PROPERTIES
    PREFIX "lib"
    SUFFIX ".so"
    LIBRARY_OUTPUT_DIRECTORY "${_build_dir}"
    INSTALL_RPATH "${_rpath}")
  install(TARGETS ${target} LIBRARY DESTINATION ${_dest})
endfunction()

# kalibr_install_python_package(<package name> <source dir>)
# Installs the pure Python sources of a package, and mirrors them into the
# build tree so that PYTHONPATH=<build>/python works without installing.
function(kalibr_install_python_package package src_dir)
  get_filename_component(_src "${src_dir}" ABSOLUTE)
  install(DIRECTORY ${_src}/
    DESTINATION ${KALIBR_PYTHON_INSTALL_DIR}/${package}
    FILES_MATCHING PATTERN "*.py"
    PATTERN "__pycache__" EXCLUDE)
  file(GLOB_RECURSE _py RELATIVE ${_src} CONFIGURE_DEPENDS ${_src}/*.py)
  foreach(_f ${_py})
    configure_file(${_src}/${_f} ${KALIBR_PYTHON_BUILD_DIR}/${package}/${_f} COPYONLY)
  endforeach()
endfunction()

# kalibr_add_gtest(<name> SOURCES <src>... [DEPS <target>...] [WORKING_DIRECTORY <dir>])
function(kalibr_add_gtest name)
  if(NOT KALIBR_BUILD_TESTS)
    return()
  endif()
  cmake_parse_arguments(ARG "" "WORKING_DIRECTORY" "SOURCES;DEPS" ${ARGN})
  add_executable(${name} ${ARG_SOURCES})
  target_compile_definitions(${name} PRIVATE GTEST_USE_OWN_TR1_TUPLE=0)
  target_link_libraries(${name} PRIVATE ${ARG_DEPS} GTest::gtest Threads::Threads)
  if(NOT ARG_WORKING_DIRECTORY)
    # Tests write serialization files into their working directory.
    set(ARG_WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
  endif()
  add_test(NAME ${name} COMMAND ${name} WORKING_DIRECTORY ${ARG_WORKING_DIRECTORY})
endfunction()
