// ads1256.h
#ifndef ADS1256_H
#define ADS1256_H

#include <stdint.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"

#define ADS1256_GAIN_1  0
#define ADS1256_GAIN_2  1
#define ADS1256_GAIN_4  2
#define ADS1256_GAIN_8  3
#define ADS1256_GAIN_16 4
#define ADS1256_GAIN_32 5
#define ADS1256_GAIN_64 6

#define ADS1256_30000SPS 0xF0
#define ADS1256_15000SPS 0xE0
#define ADS1256_7500SPS  0xD0
#define ADS1256_3750SPS  0xC0
#define ADS1256_2000SPS  0xB0
#define ADS1256_1000SPS  0xA1
#define ADS1256_500SPS   0x92
#define ADS1256_100SPS   0x82
#define ADS1256_60SPS    0x72
#define ADS1256_50SPS    0x63
#define ADS1256_30SPS    0x53
#define ADS1256_25SPS    0x43
#define ADS1256_15SPS    0x33
#define ADS1256_10SPS    0x20
#define ADS1256_5SPS     0x13
#define ADS1256_2d5SPS   0x03

#define REG_STATUS 0
#define REG_MUX    1
#define REG_ADCON  2
#define REG_DRATE  3
#define REG_IO     4
#define REG_OFC0   5
#define REG_OFC1   6
#define REG_OFC2   7
#define REG_FSC0   8
#define REG_FSC1   9
#define REG_FSC2   10

#define CMD_WAKEUP   0x00
#define CMD_RDATA    0x01
#define CMD_RDATAC   0x03
#define CMD_SDATAC   0x0F
#define CMD_RREG     0x10
#define CMD_WREG     0x50
#define CMD_SELFCAL  0xF0
#define CMD_SELFOCAL 0xF1
#define CMD_SELFGCAL 0xF2
#define CMD_SYSOCAL  0xF3
#define CMD_SYSGCAL  0xF4
#define CMD_SYNC     0xFC
#define CMD_STANDBY  0xFD
#define CMD_RESET    0xFE

typedef struct {
    spi_inst_t *spi;
    uint cs_pin;
    uint drdy_pin;
    uint pdwn_pin;
    uint baudrate;
    bool debug;
    int32_t raw[8];
    bool read_flag;
    uint8_t num_of_chans;
    uint8_t next_chan;
} ADS1256_t;

void ADS1256_Init(ADS1256_t *ads, spi_inst_t *spi, uint cs_pin, uint drdy_pin, uint pdwn_pin, uint baudrate, bool debug);
int ADS1256_ReadChipID(ADS1256_t *ads);
int ADS1256_WaitDRDY(ADS1256_t *ads);
void ADS1256_Reset(ADS1256_t *ads);
int32_t ADS1256_Parse_ADC_Data(uint8_t buf[3]);
int32_t ADS1256_Read_ADC_Data(ADS1256_t *ads);
void ADS1256_SetChannel(ADS1256_t *ads, uint8_t p_chan, uint8_t n_chan);
void ADS1256_ConfigADC(ADS1256_t *ads, uint8_t gain, uint8_t drate);
void ADS1256_SetDiffChannel(ADS1256_t *ads, uint8_t channel);
int32_t ADS1256_GetChannelValue(ADS1256_t *ads, uint8_t p_chan, uint8_t n_chan);
void ADS1256_GetAll(ADS1256_t *ads, int32_t values[8]);
void ADS1256_CycleRead(ADS1256_t *ads);
void spi_write_read_bytes(ADS1256_t *ads, uint8_t *tx_buf, uint tx_len, uint8_t *rx_buf, uint rx_len);
void write_reg(ADS1256_t *ads, uint8_t reg, uint8_t data);
void read_reg(ADS1256_t *ads, uint8_t reg, uint8_t *data, uint n);

#endif