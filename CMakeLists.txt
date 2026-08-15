cmake_minimum_required(VERSION 3.25)
project(Praxis VERSION 0.4.1 LANGUAGES CXX)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
enable_testing()

option(PRAXIS_ENABLE_WARNINGS "Enable strict warning baseline." ON)
option(PRAXIS_ENABLE_WERROR "Treat warnings as errors." OFF)
option(PRAXIS_ENABLE_SANITIZERS "Enable ASan and UBSan." OFF)

add_library(praxis_project_options INTERFACE)

if(PRAXIS_ENABLE_WARNINGS)
    if(MSVC)
        target_compile_options(praxis_project_options INTERFACE /W4 /permissive-)
    else()
        target_compile_options(praxis_project_options INTERFACE -Wall -Wextra -Wpedantic)
    endif()
endif()

if(PRAXIS_ENABLE_WERROR)
    if(MSVC)
        target_compile_options(praxis_project_options INTERFACE /WX)
    else()
        target_compile_options(praxis_project_options INTERFACE -Werror)
    endif()
endif()

if(PRAXIS_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(praxis_project_options INTERFACE
        -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(praxis_project_options INTERFACE
        -fsanitize=address,undefined -fno-omit-frame-pointer)
endif()

add_library(praxis_core STATIC
    src/core/GovernanceBaseline.cpp
    src/core/CommandRegistry.cpp
    src/cli/Commands.cpp
    src/dashboard/DashboardSnapshot.cpp
    src/dashboard/ReadOnlyHttpServer.cpp
    src/targets/TargetRegistry.cpp
    src/observation/ExternalObservation.cpp
    src/action/ActionPlan.cpp
    src/workspace/ProjectWorkspace.cpp
    src/workspace/GitSyncStatus.cpp
)

target_include_directories(praxis_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_compile_definitions(praxis_core PUBLIC
    PRAXIS_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
target_link_libraries(praxis_core PUBLIC praxis_project_options)

add_executable(sister-ops
    apps/sister-ops/main.cpp
)
target_link_libraries(sister-ops PRIVATE praxis_core praxis_project_options)

add_executable(praxis apps/praxis/main.cpp)
target_link_libraries(praxis PRIVATE praxis_core praxis_project_options)

# Compatibility alias during the SisTer-HOA -> Praxis transition.
add_executable(hoa apps/praxis/main.cpp)
target_link_libraries(hoa PRIVATE praxis_core praxis_project_options)

add_executable(PraxisCoreTests
    tests/core/GovernanceBaselineTests.cpp
)
target_link_libraries(PraxisCoreTests PRIVATE praxis_core praxis_project_options)

add_test(NAME core_governance_tests COMMAND PraxisCoreTests)

add_executable(PraxisHelpTests
    tests/cli/HelpCommandTests.cpp
)
target_link_libraries(PraxisHelpTests PRIVATE praxis_core praxis_project_options)
target_compile_definitions(PraxisHelpTests PRIVATE
    PRAXIS_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
add_test(NAME cli_help_tests COMMAND PraxisHelpTests)

add_executable(PraxisDashboardTests
    tests/dashboard/DashboardReadOnlyTests.cpp
)
target_link_libraries(PraxisDashboardTests PRIVATE praxis_core praxis_project_options)
target_compile_definitions(PraxisDashboardTests PRIVATE
    PRAXIS_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
add_test(NAME dashboard_read_only_tests COMMAND PraxisDashboardTests)

add_executable(PraxisWorkspaceTests tests/workspace/ProjectWorkspaceTests.cpp)
target_link_libraries(PraxisWorkspaceTests PRIVATE praxis_core praxis_project_options)
add_test(NAME workspace_tests COMMAND PraxisWorkspaceTests)

add_test(
    NAME methodology_bootstrap_state_tests
    COMMAND
        ${Python3_EXECUTABLE}
        ${CMAKE_CURRENT_SOURCE_DIR}/harness/scenarios/run_pbg_001_matrix.py
        --phase candidate
        --output ${CMAKE_CURRENT_BINARY_DIR}/pbg-001-ctest
)
