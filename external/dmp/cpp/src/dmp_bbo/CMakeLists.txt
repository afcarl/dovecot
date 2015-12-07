file(GLOB SOURCES runEvolutionaryOptimizationParallel.cpp CostFunctionWrapper.cpp) 
add_library(dmp_bbo ${SOURCES})
install(TARGETS dmp_bbo DESTINATION lib)

target_link_libraries(dmp_bbo
    bbo 
  )

file(GLOB HEADERS_TASK TaskViapoint*.h*)
install(FILES ${HEADERS_TASK} DESTINATION include/taskviapoint)


file(GLOB SOURCES_TASK TaskViapoint*.cpp) 
add_library(taskviapoint ${SOURCES_TASK})
install(TARGETS taskviapoint DESTINATION lib)

file(GLOB HEADERS_TASK TaskViapoint*.h*)
install(FILES ${HEADERS_TASK} DESTINATION include/taskviapoint)

add_subdirectory(demos)
IF(CMAKE_BUILD_TYPE MATCHES Debug)
    add_subdirectory(tests)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug)
