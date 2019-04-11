#!/usr/bin/python
# coding: utf-8

import os
import sys
import signal
import time
import serial
import datetime
import struct
import socket
import RPi.GPIO as GPIO
import time
import threading

class Value:
    x_val = 0
    y_val = 0
    z_val = 0


if __name__ == "__main__":

    LED = 20
    LED21 = 21
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(LED21, GPIO.OUT)
    GPIO.setwarnings(False)
    
    #timeout = None (wait forever)
    #timeout = 0 (Non-blocking)

    ser = serial.Serial('/dev/serial0', 921600, timeout=1) 

    print ("Starting up")
    
    f = open('/home/data.csv', 'a')    
    
    
    while True:
        
        readOut = ''
        #ser.flush() #flush the buffer
        ser.flushInput()
        
        dt1 = datetime.datetime.now()
        
        GPIO.output(LED, GPIO.HIGH)
        GPIO.output(LED21, GPIO.HIGH)
        ser.write(serial.to_bytes([0x04, 0x6E, 0x82, 0x9C]))
                      
                
        GPIO.output(LED, GPIO.LOW)                 
        GPIO.output(LED21, GPIO.LOW)
        
        #size = ser.inWaiting()
        
        readOut = ser.read(3078)            
        
        dt2 = datetime.datetime.now()        
        # print(dt2 - dt1)
         
        new_value = Value()         
        signal_data = []

        
        
    
        try:
            result = struct.unpack_from('<bbh', readOut, 0)            
            count_point = result[2];
            # print(count_point)
            fmt = '<%dQ' % count_point
            result = struct.unpack_from(fmt, readOut, 4)                 
            # print(struct.calcsize(fmt))
            
            # t = dt1.strftime("%f")
            
            for point in result:                
                
                
                f.write(str(dt2));                
                # f.write(str("{0}-{1}-{2} {3}:{4}:{5}.{6}".format(dt1.strftime("%Y"), dt1.strftime("%m"), dt1.strftime("%d"), dt1.strftime("%H"), dt1.strftime("%M"), dt1.strftime("%S"), t)))                
                #f.write(str("{0}-{1}-{2} {3}:{4}:{5}:{6}".format(dt1.year, datetime.date.today().strftime("%m"), dt1.day, dt1.hour, dt1.minute, dt1.second, t)))                
                #f.write(str("{}-{}-{} {}:{}:{}".format(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second)))                
                #f.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))                
                f.write(str(';'))
                
                dt2 += datetime.timedelta(microseconds=157)
                
                
                x = point & 0x1FFFFF                
                
                y = (point >> 21)                
                y = y & (0x1FFFFF)
                                
                z = point >> 42
                z = z & (0x1FFFFF)

                if x > 0xFFFFF: 
                    x = x - 0x200000
                if y > 0xFFFFF: 
                    y = y - 0x200000
                if z > 0xFFFFF: 
                    z = z - 0x200000
                
                
                # f.write(str(dt1));
                # f.write(str(';'))
                
                f.write(str(x) + ';')
                f.write(str(y) + ';')
                f.write(str(z) + ';\n')
                
                # f.write(str(point) + ';\n')
                
            
        except Exception as e:
            print(e)
            # time.sleep(0.1)
            #pass
        

        
        
        
        #time.sleep(0.1)


        