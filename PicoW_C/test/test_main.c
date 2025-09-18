// test_main.c
#include "pico/stdlib.h"
#include "test_ads1256.c"

int main() {
    stdio_init_all();
    test_init();
    test_read_chip_id();
    test_set_channel();
    while (1) tight_loop_contents();
}