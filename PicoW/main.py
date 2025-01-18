#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import ADS1256
import sys
import config
import csv
import temp_conv
import coefficients


#Initiate the digital pins; Initiate the ADS1256 module.
ADC = ADS1256.ADS1256()
if (config.module_init() != 0):
    sys.exit()
if(ADC.ADS1256_init() != 0):
    sys.exit()


# Initiate the csv and give the name
#file_name = 'test.csv'
#csv.init_file(file_name)


#setup calibration coefficients for each ADC channel
chan = []
for i in range(0, 8):
    chan.append(temp_conv.channel_cal(coefficients.channel[i][0], coefficients.channel[i][1]))


while(1):
    raw = ADC.ADS1256_cycle_read()     #fetch raw data from ADC
    read = [time.ticks_ms()]           #initate read. (also take the time in ms)
    #read = ""
    
    for i in range(0, 8):              #convert ADC reading to temp using calibrattion coefficients
        read.append(chan[i].convert(raw[i]))
    
    #read.extend(raw)                  #add raw data to read
    #csv.write_line(file_name, read)    #write the data (read) to the csv
    print(read) 

