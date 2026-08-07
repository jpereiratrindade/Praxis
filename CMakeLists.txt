cmake_minimum_required(VERSION 3.25)
project(SisTerHOA VERSION 0.4.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
enable_testing()

option(SISTER_HOA_ENABLE_WARNINGS "Enable strict warning baseline." ON)
option(SISTER_HOA_ENABLE_WERROR "Treat warnings as errors." OFF)
option(SISTER_HOA_ENABLE_SANITIZERS "Enable ASan and UBSan." OFF)

add_library(sister_hoa_project_options INTERFACE)

if(SISTER_HOA_ENABLE_WARNINGS)
    if(MSVC)
        target_compile_options(sister_hoa_project_options INTERFACE /W4 /permissive-)
    else()
        target_compile_options(sister_hoa_project_options INTERFACE -Wall -Wextra -Wpedantic)
    endif()
endif()

if(SISTER_HOA_ENABLE_WERROR)
    if(MSVC)
        target_compile_options(sister_hoa_project_options INTERFACE /WX)
    else()
        target_compile_options(sister_hoa_project_options INTERFACE -Werror)
    endif()
endif()

if(SISTER_HOA_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(sister_hoa_project_options INTERFACE
        -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(sister_hoa_project_options INTERFACE
        -fsanitize=address,undefined -fno-omit-frame-pointer)
endif()

add_library(sister_hoa_core STATIC
    src/core/GovernanceBaseline.cpp
    src/core/CommandRegistry.cpp
    src/cli/Commands.cpp
    src/dashboard/DashboardSnapshot.cpp
    src/dashboard/ReadOnlyHttpServer.cpp
    src/targets/TargetRegistry.cpp
    src/observation/ExternalObservation.cpp
    src/action/ActionPlan.cpp
)

target_include_directories(sister_hoa_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_compile_definitions(sister_hoa_core PUBLIC
    SISTER_HOA_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
target_link_libraries(sister_hoa_core PUBLIC sister_hoa_project_options)

add_executable(sister-ops
    apps/sister-ops/main.cpp
)
target_link_libraries(sister-ops PRIVATE sister_hoa_core sister_hoa_project_options)

add_executable(SisTerHOACoreTests
    tests/core/GovernanceBaselineTests.cpp
)
target_link_libraries(SisTerHOACoreTests PRIVATE sister_hoa_core sister_hoa_project_options)

add_test(NAME core_governance_tests COMMAND SisTerHOACoreTests)

add_executable(SisTerHOAHelpTests
    tests/cli/HelpCommandTests.cpp
)
target_link_libraries(SisTerHOAHelpTests PRIVATE sister_hoa_core sister_hoa_project_options)
target_compile_definitions(SisTerHOAHelpTests PRIVATE
    SISTER_HOA_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
add_test(NAME cli_help_tests COMMAND SisTerHOAHelpTests)

add_executable(SisTerHOADashboardTests
    tests/dashboard/DashboardReadOnlyTests.cpp
)
target_link_libraries(SisTerHOADashboardTests PRIVATE sister_hoa_core sister_hoa_project_options)
target_compile_definitions(SisTerHOADashboardTests PRIVATE
    SISTER_HOA_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
add_test(NAME dashboard_read_only_tests COMMAND SisTerHOADashboardTests)
