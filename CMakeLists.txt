cmake_minimum_required(VERSION 3.16)
project(simu_tp2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(tp2_core INTERFACE)
target_include_directories(tp2_core INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/src)

enable_testing()
add_executable(test_periodic_geometry tests/test_periodic_geometry.cpp)
target_link_libraries(test_periodic_geometry PRIVATE tp2_core)
add_test(NAME periodic_geometry COMMAND test_periodic_geometry)

add_executable(test_neighbor_search_bruteforce tests/test_neighbor_search_bruteforce.cpp)
target_link_libraries(test_neighbor_search_bruteforce PRIVATE tp2_core)
add_test(NAME neighbor_search_bruteforce COMMAND test_neighbor_search_bruteforce)

add_executable(test_neighbor_search_cim tests/test_neighbor_search_cim.cpp)
target_link_libraries(test_neighbor_search_cim PRIVATE tp2_core)
add_test(NAME neighbor_search_cim COMMAND test_neighbor_search_cim)

add_executable(test_rules tests/test_rules.cpp)
target_link_libraries(test_rules PRIVATE tp2_core)
add_test(NAME rules COMMAND test_rules)

add_executable(test_time_step tests/test_time_step.cpp)
target_link_libraries(test_time_step PRIVATE tp2_core)
add_test(NAME time_step COMMAND test_time_step)

add_executable(test_observables tests/test_observables.cpp)
target_link_libraries(test_observables PRIVATE tp2_core)
add_test(NAME observables COMMAND test_observables)

add_executable(test_simulation tests/test_simulation.cpp)
target_link_libraries(test_simulation PRIVATE tp2_core)
add_test(NAME simulation COMMAND test_simulation)

add_executable(test_mean_neighbors tests/test_mean_neighbors.cpp)
target_link_libraries(test_mean_neighbors PRIVATE tp2_core)
add_test(NAME mean_neighbors COMMAND test_mean_neighbors)

# Regresion diagnostica del consenso del votante sin ruido: se compila pero
# no se registra con add_test a proposito. No tiene un assert rigido sobre
# alcanzar consenso (solo sobre invariantes que si serian un bug real), asi
# que no corresponde volverla parte del pase/fallo automatico de CTest; se
# ejecuta explicitamente y se documenta su salida (ver 02_motor_y_algoritmos.md
# y 03_validaciones.md).
add_executable(voter_consensus_regression tests/voter_consensus_regression.cpp)
target_link_libraries(voter_consensus_regression PRIVATE tp2_core)
