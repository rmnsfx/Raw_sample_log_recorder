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


lock = threading.Lock()

data = []
big_data = []
    
def writer():
            
        global big_data
    # with lock:
        # time.sleep(30)
        
        file_name = str('/home/{}.csv'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        # file_name = str('/home/{}.csv'.format(datetime.datetime.now().strftime("%Y-%m-%d %H")))
        f = open(file_name, 'a')   
        
        dt2 = datetime.datetime.now()
            
        print(file_name, len(big_data))
        
        # for point in data[0:length]:    
        for point in big_data:    
        
            f.write(str(dt2));
            f.write(str(';'))                    
                
            f.write(str(point.x_val) + ';')
            f.write(str(point.y_val) + ';')
            f.write(str(point.z_val) + ';\n')
            
            dt2 += datetime.timedelta(microseconds=125)
        
        
        f.close()
        big_data *= 0
    
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data    
    

        
    
if __name__ == "__main__":

    write_flag = 0     

    # LED = 20
    # LED21 = 21
    # GPIO.cleanup()
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(LED, GPIO.OUT)
    # GPIO.setup(LED21, GPIO.OUT)
    # GPIO.setwarnings(False)
    
    #timeout = None (wait forever)
    #timeout = 0 (Non-blocking)

    # ser = serial.Serial('/dev/serial0', 921600, timeout=0.5) 
    
    send_data = '\x04\x6E\x82\x9C'
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    conn.connect(("192.168.5.241", 750))
    conn.settimeout(500)
    
    print ("Starting up")    
    
    i = 0
    
    
    while True:
        
        time1 = datetime.datetime.now()        
        
        # readOut = ''                     
        
        # ser.flush() #flush the buffer
        # ser.flushInput()
                        
        # GPIO.output(LED, GPIO.HIGH)
        # GPIO.output(LED21, GPIO.HIGH)
                
        # ser.write(serial.to_bytes([0x04, 0x6E, 0x82, 0x9C]))
        # ser.write(serial.to_bytes([0x01, 0x6E, 0x81, 0xCC]))
        
                
        conn.sendall(send_data)
        
                
        # GPIO.output(LED, GPIO.LOW)                 
        # GPIO.output(LED21, GPIO.LOW)        
        # size = ser.inWaiting()             
        # readOut = ser.read(3078)     

        # readOut = conn.recvall(3078)
        readOut = recvall(conn, 3078)
        

        
    
        # if len(readOut) >= 0 or readOut != None:
        try:
            # result = struct.unpack_from('<bbh', readOut, 0)            
            # count_point = result[2];
            # print(count_point)
            # fmt = '<%dQ' % count_point
            fmt = '<%dQ' % 384
            result = struct.unpack_from(fmt, readOut, 4)                 
            # print(struct.calcsize(fmt))
            
            
            
            for point in result:                
                
                
                # f.write(str(dt2));                
                # f.write(str("{0}-{1}-{2} {3}:{4}:{5}.{6}".format(dt1.strftime("%Y"), dt1.strftime("%m"), dt1.strftime("%d"), dt1.strftime("%H"), dt1.strftime("%M"), dt1.strftime("%S"), t)))                
                #f.write(str("{0}-{1}-{2} {3}:{4}:{5}:{6}".format(dt1.year, datetime.date.today().strftime("%m"), dt1.day, dt1.hour, dt1.minute, dt1.second, t)))                
                #f.write(str("{}-{}-{} {}:{}:{}".format(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute, dt1.second)))                
                #f.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))                
                # f.write(str(';'))
                
                # dt2 += datetime.timedelta(microseconds=157)
                
                
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
                
                values = Value()
                values.x_val = int(x)
                values.y_val = int(y)
                values.z_val = int(z)
                
                data.append(values)      
                

                    
                    
            
        except Exception as e:
            print(e)

        
        else:        

            
            # print(len(big_data))
            # print(len(data))
            if i == 2500:
                # writer(data) 
                big_data = data[:]
                # my_thread = threading.Thread(target=writer, args=(big_data,))                
                my_thread = threading.Thread(target=writer)                
                my_thread.start()
                i = 0
                data *= 0
            else:
                i += 1
                
        # time.sleep(0.09)
            
            # if len(big_data) >= 240000:
                # del big_data[:len(data)]
                # del big_data[:len(data)]
                # big_data.pop(0)
                
        # finally:        
            # data *= 0
            
            
        time2 = datetime.datetime.now()        
        print(time2 - time1)            
        
        
