################################################################################
file(GLOB SOURCES FunctionApproximator.cpp Parameterizable.cpp MetaParameters.cpp ModelParameters.cpp *LWR.cpp *GMR.cpp *IRFRLS.cpp deserializeFunctionApproximator.cpp) 
if(HAVE_LWPR_HH)
  message("HAVE_LWPR_HH")
  file(GLOB SOURCES ${SOURCES} *LWPR.cpp) 
endif()

################################################################################
add_library(functionapproximators ${SOURCES})
install(TARGETS functionapproximators DESTINATION lib)

file(GLOB HEADERS *.h*)
if(HAVE_LWPR_HH)
  file(GLOB HEADERS ${HEADERS} *LWPR.h*) 
endif()
install(FILES ${HEADERS} DESTINATION include/functionapproximators)

add_subdirectory(demos)
IF(CMAKE_BUILD_TYPE MATCHES Debug)
    add_subdirectory(tests)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug) 

