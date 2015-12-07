CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE "RELEASE")
ENDIF()

set(APPLE true)

if(APPLE)
    execute_process(COMMAND python-config --prefix
                    OUTPUT_VARIABLE PYTHON_INCLUDE_DIRS)
    string(STRIP ${PYTHON_INCLUDE_DIRS} PYTHON_INCLUDE_DIRS)
    set(PYTHON_INCLUDE_DIRS "${PYTHON_INCLUDE_DIRS}/include/python2.7/")
    execute_process(COMMAND python-config --prefix
                    OUTPUT_VARIABLE PYTHON_LIBRARIES)
    string(STRIP ${PYTHON_LIBRARIES} PYTHON_LIBRARIES)
    set(PYTHON_LIBRARIES "${PYTHON_LIBRARIES}/lib/libpython2.7.so")
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
    FIND_PACKAGE(Boost 1.55.0 COMPONENTS python filesystem system regex)

    ADD_LIBRARY(pydmp SHARED main.cpp src/dmp/demos/pydmp.cpp GenericList.cpp)
    TARGET_LINK_LIBRARIES(pydmp dmp functionapproximators dynamicalsystems ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
ELSEIF(NOT Boost_FOUND)
    MESSAGE(FATAL_ERROR "Unable to find correct Boost version. Did you set BOOST_ROOT?")
ENDIF()


file(GLOB SOURCES *.cpp)
add_library(dmp ${SOURCES})

install(TARGETS dmp DESTINATION lib)
file(GLOB HEADERS *.h*)
install(FILES ${HEADERS} DESTINATION include/dmp)

add_subdirectory(demos)
IF(CMAKE_BUILD_TYPE MATCHES Debug)
    add_subdirectory(tests)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug)
