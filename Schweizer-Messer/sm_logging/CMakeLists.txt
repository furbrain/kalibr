kalibr_add_library(sm_logging
  SOURCES
    src/Logger.cpp
    src/StdOutLogger.cpp
    src/LoggingEvent.cpp
    src/LoggingGlobals.cpp
    src/Formatter.cpp
    src/Tokens.cpp
  DEPS Boost::system Boost::thread Boost::regex)

kalibr_add_gtest(sm_logging-test
  SOURCES test/test_main.cpp test/logTest.cpp
  DEPS sm_logging)
