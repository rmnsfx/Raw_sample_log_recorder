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



signal_data = []
int_signal = []

def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]

if __name__ == "__main__":
    
    #y = [0x07, 0x6E, 0x82, 0x6C]
    #data = pickle.dumps(y)
    data = '\x07\x6E\x82\x6C'

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("192.168.5.131", 750))


    f = open('/home/pi/data.log', 'a')
    # f.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    while True:

        dt1 = datetime.datetime.now()

        conn.send(data)
        pack = conn.recv(3078)



        for x in pack:
            #signal_data.append( int( x.encode("hex"), 32 ) )
            signal_data.append( x.encode("hex") )

        # try:
        #     print(signal_data[0], signal_data[1], signal_data[2],  signal_data[3])
        # except Exception as e:
        #     print(e)

        value = 0
        valueX = 0
        valueY = 0
        valueZ = 0

        try:
            address = signal_data[0]
            func_code = signal_data[1]
            count_point = signal_data[2] + signal_data[3]
            # print(address, func_code, count_point)
            i = 4
            j = 0
            x = 0
            y = 0
            z = 0


            while i < 3076:



                # value1 = int(signal_data[4], 16)
                # value2 = int(signal_data[5], 16)
                # value = int((value2 << 8) + value1)

                j = 0
                while j < i:
                     value += int(signal_data[j], 16)
                     j += 1

                value = swap32(value)

                x =  (value & 0x1FFFFF)
                y = int((value >> 21) & 0x1FFFFF)
                z = int((value >> 42) & 0x1FFFFF)

                if x > 0xFFFFF: x - 0x200000
                if y > 0xFFFFF: y - 0x200000
                if z > 0xFFFFF: z - 0x200000

                i += 8


                #print(x)


            #print(address, func_code, count_point)
            print(x)

        except Exception as e:
            print(e)





            #value_data = long ( long(value_data.encode('hex'), 32) & 0x1FFFFF)

        # if (value_data > 0xFFFFF):
        #     value_data - 0x200000



        for x in pack:
            # print(x.encode("hex"))
            f.write(str(x.encode("hex")))
            f.write(str(' '))

        f.write(str("work" + '\n\n'))

        dt2 = datetime.datetime.now()
        #print(dt2 - dt1)

        time.sleep(0.2)


    f.close()
    conn.close()
