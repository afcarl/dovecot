set(CMAKE_DISABLE_SOURCE_CHANGES ON)
set(CMAKE_DISABLE_IN_SOURCE_BUILD ON)

# Project name is not mandatory, but you should use it
project(OO_DMP_BBO)

# States that CMake required version must be greater than 2.6
cmake_minimum_required(VERSION 2.6)

set(CMAKE_CXX_FLAGS "-Wall -std=c++0x")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# Appends the cmake/modules path inside the MAKE_MODULE_PATH variable which stores the
# directories of additional CMake modules (ie. MacroOutOfSourceBuild.cmake):
set(CMAKE_MODULE_PATH ${oo_dmp_bbo_SOURCE_DIR}/cmake/modules ${CMAKE_MODULE_PATH})

include_directories(${CMAKE_SOURCE_DIR}/src)
link_directories(${CMAKE_SOURCE_DIR}/lib)

IF(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  SET(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR} CACHE PATH "Comment" FORCE)
ENDIF(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)




include_directories(${CMAKE_SOURCE_DIR}/../thirdparty/lwpr/include)    
get_property(inc_dirs DIRECTORY PROPERTY INCLUDE_DIRECTORIES)
find_file(HAVE_LWPR_HH lwpr.hh PATHS ${inc_dirs})


if(HAVE_LWPR_HH)
    message("-- Found LWPR headers")  
    link_directories(${CMAKE_SOURCE_DIR}/../thirdparty/lwpr//src/.libs)    
    get_property(lib_dirs DIRECTORY PROPERTY LINK_DIRECTORIES)
    find_library(HAVE_LWPR lwpr PATHS ${lib_dirs})
    if(HAVE_LWPR)
        message("-- Found LWPR library")  
        SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DUSE_LWPR")
        SET(LWPR_LIBRARIES lwpr)
    else()
        message("-- Could not find (optional) LWPR library")
    endif()
else()
    message("-- Could not find (optional) LWPR headers")
endif()

find_package( Boost 1.34 COMPONENTS filesystem system regex)
link_directories ( ${Boost_LIBRARY_DIRS} )
include_directories ( ${Boost_INCLUDE_DIRS} )



add_subdirectory(src)

option(BUILD_DOCUMENTATION "Use Doxygen to create the HTML based API documentation" ON)
if(BUILD_DOCUMENTATION)
  FIND_PACKAGE(Doxygen)
  if (NOT DOXYGEN_FOUND)
    message(FATAL_ERROR 
      "Doxygen is needed to build the documentation. Please install it correctly")
  endif()
  #-- Configure the Template Doxyfile for our specific project
  configure_file(${CMAKE_SOURCE_DIR}/docs/Doxyfile.in 
                 ${PROJECT_BINARY_DIR}/Doxyfile  @ONLY IMMEDIATE)
  #-- Add a custom target to run Doxygen when ever the project is built
  add_custom_target (Docs  
  										COMMAND ${DOXYGEN_EXECUTABLE} ${PROJECT_BINARY_DIR}/Doxyfile
  										SOURCES ${PROJECT_BINARY_DIR}/Doxyfile)
  # IF you do NOT want the documentation to be generated EVERY time you build the project
  # then leave out the 'ALL' keyword from the above command.
endif()

