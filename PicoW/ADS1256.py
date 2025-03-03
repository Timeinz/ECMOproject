import config
import time
import coefficients
from machine import Pin
from printhandler import PrintHandler

ph = PrintHandler()
ScanMode = 0

# gain channel
ADS1256_GAIN_E = {'ADS1256_GAIN_1'  : 0,    # GAIN   1
                  'ADS1256_GAIN_2'  : 1,	# GAIN   2
                  'ADS1256_GAIN_4'  : 2,	# GAIN   4
                  'ADS1256_GAIN_8'  : 3,	# GAIN   8
                  'ADS1256_GAIN_16' : 4,    # GAIN  16
                  'ADS1256_GAIN_32' : 5,    # GAIN  32
                  'ADS1256_GAIN_64' : 6,    # GAIN  64
                 }

# data rate
ADS1256_DRATE_E = {'ADS1256_30000SPS'   : 0xF0, # reset the default values
                   'ADS1256_15000SPS'   : 0xE0,
                   'ADS1256_7500SPS'    : 0xD0,
                   'ADS1256_3750SPS'    : 0xC0,
                   'ADS1256_2000SPS'    : 0xB0,
                   'ADS1256_1000SPS'    : 0xA1,
                   'ADS1256_500SPS'     : 0x92,
                   'ADS1256_100SPS'     : 0x82,
                   'ADS1256_60SPS'      : 0x72,
                   'ADS1256_50SPS'      : 0x63,
                   'ADS1256_30SPS'      : 0x53,
                   'ADS1256_25SPS'      : 0x43,
                   'ADS1256_15SPS'      : 0x33,
                   'ADS1256_10SPS'      : 0x20,
                   'ADS1256_5SPS'       : 0x13,
                   'ADS1256_2d5SPS'     : 0x03
                  }

# registration definition
REG_E = {'REG_STATUS'   : 0,    # x1H
         'REG_MUX'      : 1,    # 01H
         'REG_ADCON'    : 2,    # 20H
         'REG_DRATE'    : 3,    # F0H
         'REG_IO'       : 4,    # E0H
         'REG_OFC0'     : 5,    # xxH
         'REG_OFC1'     : 6,    # xxH
         'REG_OFC2'     : 7,    # xxH
         'REG_FSC0'     : 8,    # xxH
         'REG_FSC1'     : 9,    # xxH
         'REG_FSC2'     : 10,   # xxH
        }

# command definition
CMD = {'CMD_WAKEUP'     : 0x00,    # Completes SYNC and Exits Standby Mode 0000  0000 (00h)
       'CMD_RDATA'      : 0x01,    # Read Data 0000  0001 (01h)
       'CMD_RDATAC'     : 0x03,    # Read Data Continuously 0000   0011 (03h)
       'CMD_SDATAC'     : 0x0F,    # Stop Read Data Continuously 0000   1111 (0Fh)
       'CMD_RREG'       : 0x10,    # Read from REG rrr 0001 rrrr (1xh)
       'CMD_WREG'       : 0x50,    # Write to REG rrr 0101 rrrr (5xh)
       'CMD_SELFCAL'    : 0xF0,    # Offset and Gain Self-Calibration 1111    0000 (F0h)
       'CMD_SELFOCAL'   : 0xF1,    # Offset Self-Calibration 1111    0001 (F1h)
       'CMD_SELFGCAL'   : 0xF2,    # Gain Self-Calibration 1111    0010 (F2h)
       'CMD_SYSOCAL'    : 0xF3,    # System Offset Calibration 1111   0011 (F3h)
       'CMD_SYSGCAL'    : 0xF4,    # System Gain Calibration 1111    0100 (F4h)
       'CMD_SYNC'       : 0xFC,    # Synchronize the A/D Conversion 1111   1100 (FCh)
       'CMD_STANDBY'    : 0xFD,    # Begin Standby Mode 1111   1101 (FDh)
       'CMD_RESET'      : 0xFE,    # Reset to Power-Up Values 1111   1110 (FEh)
      }

class ADS1256:
    def __init__(self, spi):
        self.CS             = Pin(config.ADC_CS, Pin.OUT)
        self.DRDY           = Pin(config.DRDY_PIN, Pin.IN, Pin.PULL_DOWN)
        self.RST            = Pin(config.RST_PIN, Pin.OUT)
        self.PDWN           = Pin(config.PDWN_PIN, Pin.OUT)
        self.flag           = False
        self.next_chan      = 1
        self.num_of_chans   = 8
        self.raw            = []
        self.read           = []
        self.read_flag      = False
        self.chan           = []
        self.spi            = spi

    class channel_cal:
        def __init__(self, c0, c1):
            self.c0 = c0
            self.c1 = c1
        
        def convert(self, x):
            temp = self.c0 * x + self.c1
            return temp
 
    def DRDY_callback(self, DRDY_irq):
        self.flag = True

    def ADS1256_init(self, ph):
        self.PDWN.value(1)
        ID = self.ADS1256_ReadChipID()
        ph.print(ID)
        if ID == 3 :
            ph.print("ID Read success")
        else:
            ph.print("ID Read failed")
            #self.lcd.putstr("ID Read failed")
            return -1
        
        #setup calibration coefficients for each ADC channel
        for i in range(0, self.num_of_chans):
            self.chan.append(self.channel_cal(coefficients.channel[i][0], coefficients.channel[i][1]))

        if self.ADS1256_WaitDRDY() != 0:
            return 1
        self.spi_writebyte([CMD['CMD_WREG'],
                              0x03,
                              0x02,
                              0x80,
                              ADS1256_GAIN_E['ADS1256_GAIN_1'],
                              ADS1256_DRATE_E['ADS1256_100SPS'],
                              CMD['CMD_RREG'],
                              0x03])
        read = self.spi_readbytes(4)
        ph.print(read)
        #self.lcd.move_to(0, 0)
        #self.lcd.putstr(str(read))
        self.spi_writebyte([CMD['CMD_SELFCAL']])
        return 0

    def ADS1256_cycle_read(self):
        '''
        ready = not self.DRDY.value()
        ph.print(ready)
        if not ready:
            return 1
        '''
        if self.next_chan == 1:
            self.raw = []
            self.read_flag = False
        
        if (self.next_chan == self.num_of_chans):
            self.next_chan = 0
            self.read_flag = True
        
        self.ADS1256_SetChannel(8,self.next_chan)
        self.spi_writebyte([CMD['CMD_SYNC'],
                                CMD['CMD_WAKEUP'],
                                CMD['CMD_RDATA']
                                ])
        self.raw.append(self.ADS1256_Read_ADC_Data())
        #ph.print(self.raw)
        self.next_chan += 1 
        return 0

    # Hardware reset
    def ADS1256_reset(self):
        self.ADS1256_WaitDRDY()
        self.spi_writebyte([CMD['CMD_RESET']])
        time.sleep_ms(1)
        
    def ADS1256_WaitDRDY(self):
        #self.flag = 1
        counter = 0
        timeout = 200000
        while(self.DRDY.value()):
            if (counter > timeout):
                #self.interrupt.irq(trigger=Pin.IRQ_FALLING, handler=None)
                ph.print("Time Out ...\n")
                #self.lcd.move_to(0, 0)
                #self.lcd.putstr("TO")
                counter = 0
                return 1
            counter += 1
        return 0
      
            
    def ADS1256_ReadChipID(self):
        if self.ADS1256_WaitDRDY() != 0:
            return -1
        
        ID = self.ADS1256_Read_data(REG_E['REG_STATUS'])
        
        ID = ID[0] >> 4
        # print 'ID',id
        return ID
    
    def ADS1256_Read_ADC_Data(self):
        buf = self.spi_readbytes(3)
        read = (buf[0]<<16) & 0xff0000
        read |= (buf[1]<<8) & 0xff00
        read |= (buf[2]) & 0xff
        if (read & 0x800000):
            read &= 0xF000000
        return read
        
    def ADS1256_SetChannel(self, PChannel, NChannel):
        #if PChannel > 8: # Channel 8 represents AINCOM
        #    return 0
        #if NChannel > 8: # Channel 8 represents AINCOM
        #    return 0
        self.ADS1256_WriteReg(REG_E['REG_MUX'], (PChannel<<4) | NChannel)
        
    def ADS1256_WriteCmd(self, reg):
        self.CS.value(0)#cs  0
        self.spi_writebyte([reg])
        self.CS.value(1)#cs 1
    
    def ADS1256_WriteReg(self, reg, data):
        #self.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        self.spi_writebyte([CMD['CMD_WREG'] | reg, 0x00, data])
        #self.delay_ms(10)
        #self.digital_write(self.cs_pin, GPIO.HIGH)#cs 1
        #self.delay_ms(10)
        
    def ADS1256_Read_data(self, reg):
        #self.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        #print([CMD['CMD_RREG'] | reg, 0x00])
        self.spi_writebyte([CMD['CMD_RREG'] | reg, 0x00])
        #self.delay_ms(1)
        data = self.spi_readbytes(1)
        #print(data)
        #self.digital_write(self.cs_pin, GPIO.HIGH)#cs 1

        return data
        
    #The configuration parameters of ADC, gain and data rate
    def ADS1256_ConfigADC(self, gain, drate):
        self.ADS1256_WaitDRDY()
        buf = [0,0,0,0,0,0,0,0]
        buf[0] = (0<<3) | (1<<2) | (0<<1)
        buf[1] = 0x08
        buf[2] = (0<<5) | (0<<3) | (gain<<0)
        buf[3] = drate
        
        self.CS.value(0)#cs  0
        self.spi_writebyte([CMD['CMD_WREG'] | 0, 0x03])
        self.spi_writebyte(buf)
        
        self.CS.value(1)#cs 1
        time.sleep_ms(1)

    def ADS1256_SetDiffChannal(self, Channal):
        if Channal == 0:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (0 << 4) | 1) 	#DiffChannal  AIN0-AIN1
        elif Channal == 1:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (2 << 4) | 3) 	#DiffChannal   AIN2-AIN3
        elif Channal == 2:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (4 << 4) | 5) 	#DiffChannal    AIN4-AIN5
        elif Channal == 3:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (6 << 4) | 7) 	#DiffChannal   AIN6-AIN7

    def ADS1256_SetMode(self, Mode):
        ScanMode = Mode

    def interrupt_routine(self):
        buf = self.spi_readbytes(3)
        read = (buf[0]<<16) & 0xff0000
        read |= (buf[1]<<8) & 0xff00
        read |= (buf[2]) & 0xff
        if (read & 0x800000):
            read &= 0xF000000
        
        print(read)
        #lcd.clear()
        self.lcd.move_to(0,0)
        self.lcd.putstr(str(read))

    def ADS1256_GetChannalValue(self, PChannel, NChannel):
        if(ScanMode == 0):# 0  Single-ended input  8 channel1 Differential input  4 channe 
            if(PChannel>8 or NChannel>8):
                return 0
            self.ADS1256_SetChannel(PChannel, NChannel)
            self.ADS1256_WriteCmd(CMD['CMD_SYNC'])
            # self.delay_ms(10)
            self.ADS1256_WriteCmd(CMD['CMD_WAKEUP'])
            # self.delay_ms(200)
            Value = self.ADS1256_Read_ADC_Data()
        else:
            if(Channel>=4):
                return 0
            self.ADS1256_SetDiffChannal(Channel)
            self.ADS1256_WriteCmd(CMD['CMD_SYNC'])
            # self.delay_ms(10) 
            self.ADS1256_WriteCmd(CMD['CMD_WAKEUP'])
            # self.delay_ms(10) 
            Value = self.ADS1256_Read_ADC_Data()
        return Value
        
    def ADS1256_GetAll(self):
        ADC_Value = [0,0,0,0,0,0,0,0]
        for i in range(0,8,1):
            ADC_Value[i] = self.ADS1256_GetChannalValue(i)
        return ADC_Value
    
    def spi_readbytes(self, nbytes):
        self.CS.value(0)
        message = self.spi.read(nbytes)
        self.CS.value(1)
        return message
    
    def spi_writebyte(self, buffer):
        self.CS.value(0)
        self.spi.write(buffer)
        self.CS.value(1)
### END OF FILE ###
    
    