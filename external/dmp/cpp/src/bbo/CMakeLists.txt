file(GLOB SOURCES *.cpp updaters/*.cpp) 
add_library(bbo ${SOURCES})

install(TARGETS bbo DESTINATION lib)
file(GLOB HEADERS *.h*)
install(FILES ${HEADERS} DESTINATION include/bbo)

add_subdirectory(demos)
IF(CMAKE_BUILD_TYPE MATCHES Debug)
	add_subdirectory(tests)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug) 

