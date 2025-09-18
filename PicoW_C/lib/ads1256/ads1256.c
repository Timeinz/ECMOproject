// ads1256.c
#include "ads1256.h"
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/spi.h"

void ADS1256_Init(ADS1256_t *ads, spi_inst_t *spi, uint cs_pin, uint drdy_pin, uint pdwn_pin, uint baudrate, bool debug) {
    ads->spi = spi;
    ads->cs_pin = cs_pin;
    ads->drdy_pin = drdy_pin;
    ads->pdwn_pin = pdwn_pin;
    ads->baudrate = baudrate;
    ads->debug = debug;
    ads->num_of_chans = 8;
    ads->next_chan = 1;
    ads->read_flag = false;

    gpio_init(cs_pin);
    gpio_set_dir(cs_pin, GPIO_OUT);
    gpio_put(cs_pin, 1);

    gpio_init(drdy_pin);
    gpio_set_dir(drdy_pin, GPIO_IN);

    gpio_init(pdwn_pin);
    gpio_set_dir(pdwn_pin, GPIO_OUT);
    gpio_put(pdwn_pin, 1);
    sleep_ms(100);

    spi_init(spi, baudrate);
    spi_set_format(spi, 8, SPI_CPOL_0, SPI_CPHA_1, SPI_MSB_FIRST);

    int id = ADS1256_ReadChipID(ads);
    if (id != 3) return;

    if (ADS1256_WaitDRDY(ads) != 0) return;

    uint8_t buf[4] = {CMD_WREG, 0x03, 0x02, 0x80};
    spi_write_read_bytes(ads, buf, 4, NULL, 0);

    write_reg(ads, REG_ADCON, ADS1256_GAIN_1); // Use config values as needed
    write_reg(ads, REG_DRATE, ADS1256_30000SPS);

    uint8_t cmd = CMD_SELFCAL;
    spi_write_read_bytes(ads, &cmd, 1, NULL, 0);
}

int ADS1256_ReadChipID(ADS1256_t *ads) {
    if (ADS1256_WaitDRDY(ads) != 0) return -1;
    uint8_t data;
    read_reg(ads, REG_STATUS, &data, 1);
    return data >> 4;
}

int ADS1256_WaitDRDY(ADS1256_t *ads) {
    uint32_t timeout = 200000;
    while (gpio_get(ads->drdy_pin)) {
        if (--timeout == 0) return 1;
    }
    return 0;
}

void ADS1256_Reset(ADS1256_t *ads) {
    ADS1256_WaitDRDY(ads);
    uint8_t cmd = CMD_RESET;
    spi_write_read_bytes(ads, &cmd, 1, NULL, 0);
    sleep_ms(1);
}

int32_t ADS1256_Parse_ADC_Data(uint8_t buf[3]) {
    int32_t read = (buf[0] << 16) | (buf[1] << 8) | buf[2];
    if (read & 0x800000) read |= 0xFF000000; // Sign extend
    return read;
}

int32_t ADS1256_Read_ADC_Data(ADS1256_t *ads) {
    uint8_t buf[3];
    uint8_t cmd = CMD_RDATA;
    spi_write_read_bytes(ads, &cmd, 1, buf, 3);
    return ADS1256_Parse_ADC_Data(buf);
}

void ADS1256_SetChannel(ADS1256_t *ads, uint8_t p_chan, uint8_t n_chan) {
    uint8_t mux = (p_chan << 4) | n_chan;
    write_reg(ads, REG_MUX, mux);
}

void ADS1256_ConfigADC(ADS1256_t *ads, uint8_t gain, uint8_t drate) {
    ADS1256_WaitDRDY(ads);
    uint8_t buf[4] = {0x00, 0x08, gain, drate};
    uint8_t cmd[2] = {CMD_WREG, 0x03};
    spi_write_read_bytes(ads, cmd, 2, NULL, 0);
    spi_write_read_bytes(ads, buf, 4, NULL, 0);
    sleep_ms(1);
}

void ADS1256_SetDiffChannel(ADS1256_t *ads, uint8_t channel) {
    uint8_t mux;
    switch (channel) {
        case 0: mux = (0 << 4) | 1; break;
        case 1: mux = (2 << 4) | 3; break;
        case 2: mux = (4 << 4) | 5; break;
        case 3: mux = (6 << 4) | 7; break;
        default: return;
    }
    write_reg(ads, REG_MUX, mux);
}

int32_t ADS1256_GetChannelValue(ADS1256_t *ads, uint8_t p_chan, uint8_t n_chan) {
    ADS1256_SetChannel(ads, p_chan, n_chan);
    uint8_t cmd_sync = CMD_SYNC;
    spi_write_read_bytes(ads, &cmd_sync, 1, NULL, 0);
    uint8_t cmd_wakeup = CMD_WAKEUP;
    spi_write_read_bytes(ads, &cmd_wakeup, 1, NULL, 0);
    return ADS1256_Read_ADC_Data(ads);
}

void ADS1256_GetAll(ADS1256_t *ads, int32_t values[8]) {
    for (uint8_t i = 0; i < 8; i++) {
        values[i] = ADS1256_GetChannelValue(ads, i, 0);
    }
}

void ADS1256_CycleRead(ADS1256_t *ads) {
    if (ads->next_chan == 1) {
        ads->read_flag = false;
    }
    if (ads->next_chan == ads->num_of_chans) {
        ads->next_chan = 0;
        ads->read_flag = true;
    }
    ADS1256_SetChannel(ads, 8, ads->next_chan); // AINCOM as 8
    uint8_t cmds[3] = {CMD_SYNC, CMD_WAKEUP, CMD_RDATA};
    uint8_t buf[3];
    uint8_t mux_cmd = CMD_WREG | REG_MUX;
    spi_write_read_bytes(ads, &mux_cmd, 1, NULL, 0);
    uint8_t mux_data[2] = {0x00, (8 << 4) | ads->next_chan}; // Adjust
    spi_write_read_bytes(ads, mux_data, 2, NULL, 0);
    spi_write_read_bytes(ads, cmds, 3, buf, 3);
    ads->raw[ads->next_chan - 1] = ADS1256_Parse_ADC_Data(buf);
    ads->next_chan++;
}

void spi_write_read_bytes(ADS1256_t *ads, uint8_t *tx_buf, uint tx_len, uint8_t *rx_buf, uint rx_len) {
    gpio_put(ads->cs_pin, 0);
    if (tx_len > 0) spi_write_blocking(ads->spi, tx_buf, tx_len);
    sleep_us(7);
    if (rx_len > 0) spi_read_blocking(ads->spi, 0, rx_buf, rx_len);
    sleep_us(2);
    gpio_put(ads->cs_pin, 1);
}

void write_reg(ADS1256_t *ads, uint8_t reg, uint8_t data) {
    uint8_t buf[3] = {CMD_WREG | reg, 0x00, data};
    spi_write_read_bytes(ads, buf, 3, NULL, 0);
}

void read_reg(ADS1256_t *ads, uint8_t reg, uint8_t *data, uint n) {
    uint8_t buf[2] = {CMD_RREG | reg, n - 1};
    spi_write_read_bytes(ads, buf, 2, NULL, 0);
    sleep_us(7); // t6 delay
    spi_write_read_bytes(ads, NULL, 0, data, n);
}