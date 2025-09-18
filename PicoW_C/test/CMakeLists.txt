add_executable(test_ads1256
    test_main.c
    test_ads1256.c
    ${CMAKE_CURRENT_LIST_DIR}/../lib/ads1256/ads1256.c
)
target_include_directories(test_ads1256 PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../lib/ads1256
)
target_link_libraries(test_ads1256 pico_stdlib hardware_spi)
pico_add_extra_outputs(test_ads1256)