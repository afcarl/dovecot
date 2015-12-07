file(GLOB SOURCES *.cpp) 
add_library(dynamicalsystems ${SOURCES})

install(TARGETS dynamicalsystems DESTINATION lib)
file(GLOB HEADERS *.h*)
install(FILES ${HEADERS} DESTINATION include/dynamicalsystems/)

add_subdirectory(demos)
IF(CMAKE_BUILD_TYPE MATCHES Debug)
    add_subdirectory(tests)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug) 

