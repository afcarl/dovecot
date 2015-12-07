CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE "RELEASE")
ENDIF()

set(CMAKE_CXX_FLAGS "-Wall -g -std=c++0x")
set(APPLE true)

link_directories ( "/home/optistem/prefix/lib" )
include_directories ( "/home/optistem/prefix/include" )

if(APPLE)
    execute_process(COMMAND python-config --prefix
                    OUTPUT_VARIABLE PYTHON_INCLUDE_DIRS)
    string(STRIP ${PYTHON_INCLUDE_DIRS} PYTHON_INCLUDE_DIRS)
    set(PYTHON_INCLUDE_DIRS "${PYTHON_INCLUDE_DIRS}/include/python2.7/")
    execute_process(COMMAND python-config --prefix
                    OUTPUT_VARIABLE PYTHON_LIBRARIES)
    string(STRIP ${PYTHON_LIBRARIES} PYTHON_LIBRARIES)
    set(PYTHON_LIBRARIES "${PYTHON_LIBRARIES}/lib/libpython2.7.dylib")
else(APPLE)
    #FIND_PACKAGE(PythonLibs 2.7 REQUIRED)
endif(APPLE)

message(STATUS "${PYTHON_INCLUDE_DIRS}")
message(STATUS "${PYTHON_LIBRARIES}")

FIND_PACKAGE(Boost 1.55.0)

IF(Boost_FOUND)
    INCLUDE_DIRECTORIES("${Boost_INCLUDE_DIRS}" "${PYTHON_INCLUDE_DIRS}" "/usr/local/include")
    SET(Boost_USE_STATIC_LIBS ON)
    SET(Boost_USE_MULTITHREADED ON)
    SET(Boost_USE_STATIC_RUNTIME OFF)
    FIND_PACKAGE(Boost 1.55.0 COMPONENTS python filesystem system serialization regex)

ELSEIF(NOT Boost_FOUND)
    MESSAGE(FATAL_ERROR "Unable to find correct Boost version. Did you set BOOST_ROOT?")
ENDIF()

#add_executable(demoDmp demoDmp.cpp)
add_executable(demoPyDmp demoPyDmp.cpp pydmp.cpp)
#target_link_libraries(demoDmp dmp functionapproximators dynamicalsystems ${Boost_LIBRARIES})
target_link_libraries(demoPyDmp dmp functionapproximators dynamicalsystems ${Boost_LIBRARIES})
#install(TARGETS demoDmp DESTINATION bin)
install(TARGETS demoPyDmp DESTINATION bin)
