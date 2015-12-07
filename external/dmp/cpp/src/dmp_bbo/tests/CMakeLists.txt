add_executable(testTaskViapoint testTaskViapoint.cpp)
target_link_libraries( testTaskViapoint dmp taskviapoint bbo ${Boost_LIBRARIES})
install(TARGETS testTaskViapoint DESTINATION bin_test)
