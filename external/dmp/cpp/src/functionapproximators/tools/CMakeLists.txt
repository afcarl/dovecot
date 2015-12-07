add_executable(trainFunctionApproximator trainFunctionApproximator.cpp)
target_link_libraries(trainFunctionApproximator functionapproximators ${LWPR_LIBRARIES} ${Boost_LIBRARIES}) # zzz
install(TARGETS trainFunctionApproximator DESTINATION bin)

add_executable(predictFunctionApproximator predictFunctionApproximator.cpp)
target_link_libraries(predictFunctionApproximator functionapproximators ${LWPR_LIBRARIES} ${Boost_LIBRARIES}) # zzz
install(TARGETS predictFunctionApproximator DESTINATION bin)
install(FILES ${CMAKE_SOURCE_DIR}/src/functionapproximators/tests/predictFunctionApproximator.py DESTINATION bin)
