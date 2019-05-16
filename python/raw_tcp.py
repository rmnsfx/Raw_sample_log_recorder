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
from threading import Timer

class Value:
    x_val = 0
    y_val = 0
    z_val = 0


lock = threading.Lock()
time1 = 0
data = []
big_data = []
dt2 = datetime.datetime.now()   
dt3 = datetime.datetime.now()
    
def writer(time):
            
        global big_data
        global dt3
                
        file_name = str('/home/{}.csv'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        # file_name = str('/home/{}.csv'.format(datetime.datetime.now().strftime("%Y-%m-%d %H")))
        f = open(file_name, 'a')   
            
        print(file_name, len(big_data))
                
        for point in big_data:    
        
            f.write(str(time));
            f.write(str(';'))                    
                
            f.write(str(point.x_val) + ';')
            f.write(str(point.y_val) + ';')
            f.write(str(point.z_val) + ';\n')
            
            time += datetime.timedelta(microseconds=125)
        

        f.close()
        big_data *= 0
        
        dt3 = time
        
        return None
                
                
    
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

    send_data = '\x04\x6E\x82\x9C'
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    conn.connect(("192.168.5.241", 750))
    conn.settimeout(500)
    
    print ("Starting up")    
    
    i = 0
    
    
    
    while True:
        
        time1 = datetime.datetime.now()        
                
        conn.sendall(send_data)

        readOut = recvall(conn, 3078)        
        
        
        try:
            # result = struct.unpack_from('<bbh', readOut, 0)            
            # count_point = result[2];
            # print(count_point)
            # fmt = '<%dQ' % count_point
            fmt = '<%dQ' % 384
            result = struct.unpack_from(fmt, readOut, 4)                 
            # print(struct.calcsize(fmt))
            
            
            
            for point in result:                
                
                values = Value()
                
                values.x_val= point & 0x1FFFFF                
                
                values.y_val = (point >> 21)                
                values.y_val = values.y_val & (0x1FFFFF)
                                
                values.z_val = point >> 42
                values.z_val = values.z_val & (0x1FFFFF)

                if values.x_val > 0xFFFFF: 
                    values.x_val = values.x_val - 0x200000
                if values.y_val > 0xFFFFF: 
                    values.y_val = values.y_val - 0x200000
                if values.z_val > 0xFFFFF: 
                    values.z_val = values.z_val - 0x200000                
                
                data.append(values)      
                    
            
        except Exception as e:
            print(e)

        
        else:        

            
            # print(len(big_data))
            # print(len(data))
            if i == 100:
                # writer(data) 
                # time1 = datetime.datetime.now()  
                big_data = data[:]                
                
                # my_thread = threading.Thread(target=writer, args=(big_data,))                
                # my_thread = threading.Thread(target=writer)                
                # my_thread = threading.Timer(5, writer)                              
                my_thread = threading.Thread(target=writer, args=(dt3,))                
                my_thread.start()
                
                print('delta = ', datetime.datetime.now() - dt3)
 
                
                
                i = 0
                data *= 0
            else:
                i += 1
                
            
        # finally:        
            # data *= 0
            
            
        time2 = datetime.datetime.now()        
        print(time2 - time1)            
        
        
