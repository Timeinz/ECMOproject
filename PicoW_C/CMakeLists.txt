# Minimum CMake version required
cmake_minimum_required(VERSION 3.13)

# Specify the board (for Pico W)
set(PICO_BOARD pico_w)

# Pull in Pico SDK (must be before project)
# include(pico_sdk_import.cmake)
include(pico-sdk/external/pico_sdk_import.cmake)

# Set path to FreeRTOS-Kernel (adjust if necessary, e.g., if it's a submodule)
set(FREERTOS_KERNEL_PATH ${CMAKE_CURRENT_LIST_DIR}/FreeRTOS-Kernel)

# Pull in FreeRTOS using the RP2040 port's import script
# include(${FREERTOS_KERNEL_PATH}/portable/ThirdParty/GCC/RP2040/FreeRTOS_Kernel_import.cmake)
include(FreeRTOS-Kernel/portable/ThirdParty/GCC/RP2040/FreeRTOS_Kernel_import.cmake)

# Project name
# project(embedded_firmware C CXX ASM)
project(pico_firmware C)

# Initialize the SDK
pico_sdk_init()

# Add subdirectories
add_subdirectory(src)
add_subdirectory(test)

# Add executable (assuming a main.c file; add more sources as needed)
add_executable(${PROJECT_NAME}
    main.c
)

# Link libraries (pico_stdlib for basic I/O, FreeRTOS-Kernel for RTOS)
target_link_libraries(${PROJECT_NAME}
    pico_stdlib
    FreeRTOS-Kernel
)

# Enable USB output, disable UART output (optional; adjust as needed)
pico_enable_stdio_usb(${PROJECT_NAME} 1)
pico_enable_stdio_uart(${PROJECT_NAME} 0)

# Add extra outputs like .uf2 for easy flashing
pico_add_extra_outputs(${PROJECT_NAME})