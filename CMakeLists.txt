cmake_minimum_required(VERSION 3.15)
project(DeepLOB_Ingestion CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags for MSVC (Windows)
if(MSVC)
    add_compile_options(/O2 /Ob2 /Oi /Ot /favor:blend)
endif()

# Locate dependencies managed by vcpkg
find_package(ixwebsocket CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

# Include directories
include_directories(include)

# Define the executable
add_executable(IngestionEngine src/cpp/main.cpp)

# Link the libraries to the executable
target_link_libraries(IngestionEngine PRIVATE 
    ixwebsocket::ixwebsocket
    nlohmann_json::nlohmann_json
    Bcrypt
)