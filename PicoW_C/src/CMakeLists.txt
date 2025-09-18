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
