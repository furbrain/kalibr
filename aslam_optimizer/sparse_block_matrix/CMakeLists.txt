kalibr_add_library(sparse_block_matrix
  SOURCES
    src/matrix_structure.cpp
    src/sparse_helper.cpp
    src/marginal_covariance_cholesky.cpp
  DEPS sm_common sm_eigen Eigen3::Eigen ${SUITESPARSE_LIBRARIES})
target_include_directories(sparse_block_matrix PUBLIC ${CHOLMOD_INCLUDE_DIR} ${SUITESPARSE_INCLUDE_DIRS})

kalibr_add_gtest(sparse_block_matrix_tests
  SOURCES
    test/test_main.cpp
    test/solver_tests.cpp
    test/sparse_block_matrix_tests.cpp
  DEPS sparse_block_matrix)
