// test_ads1256.c
#include "ads1256.h"
#include "pico/stdlib.h"
#include "hardware/spi.h"

void test_init() {
    ADS1256_t ads;
    ADS1256_Init(&ads, spi0, 10, 11, 12, 1920000, false);
    // Check if SPI and GPIO pins are configured
    if (ads.spi != spi0 || ads.cs_pin != 10 || ads.drdy_pin != 11) {
        printf("Test Init: FAILED\n");
    } else {
        printf("Test Init: PASSED\n");
    }
}

void test_read_chip_id() {
    ADS1256_t ads;
    ADS1256_Init(&ads, spi0, 10, 11, 12, 1920000, false);
    int id = ADS1256_ReadChipID(&ads);
    if (id == 3) {
        printf("Test ReadChipID: PASSED\n");
    } else {
        printf("Test ReadChipID: FAILED (ID=%d)\n", id);
    }
}

void test_set_channel() {
    ADS1256_t ads;
    ADS1256_Init(&ads, spi0, 10, 11, 12, 1920000, false);
    ADS1256_SetChannel(&ads, 0, 8); // AIN0, AINCOM
    uint8_t mux;
    read_reg(&ads, REG_MUX, &mux, 1);
    if (mux == (0 << 4) | 8) {
        printf("Test SetChannel: PASSED\n");
    } else {
        printf("Test SetChannel: FAILED (MUX=0x%x)\n", mux);
    }
}