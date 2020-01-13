import time
import serial
import binascii
import sys
import getopt
from sklearn import svm
import pandas as pd

def crc16(data):
    crc = 0xFFFF
    for p in data:
        crc = crc ^ ord(p)
        for i in range(0, 8, ):
            flag = crc & 1
            crc = crc >> 1
            if flag:
                crc = crc ^ 0xA001
    return crc

def read_data(filename):
  X = []
  df = pd.read_csv(filename, index_col="label")
  X = df.values 
  df = pd.read_csv(filename)
  Y = [x[-1] for x in df.values]
  return X, Y	
	
devi='/dev/ttyUSB0'
baudrat=115200
outtime=1
num=1
dela=0.5
show=60
myopts, args = getopt.getopt(sys.argv[1:],"d:r:o:n:t:s:")
for o, a in myopts:
	if o == '-d':
		devi=a
	if o == '-r':
		baudrat=int(a)
	if o == '-o':
		outtime=int(a)
	if o == '-n':
		num=int(a)
	if o == '-t':
		dela=float(a)
	if o == '-s':
		show=int(a)

ser = serial.Serial(devi, baudrate=baudrat, timeout=outtime)
sp = serial.Serial()
sp.port = '/dev/ttyACM0'
sp.baudrate = 9600
sp.timeout = 5
sp.open()
temper = 20

X, Y = read_data("train1.csv")
clf = svm.SVC()
clf.fit(X, Y)

while True:
    time.sleep(1.5)
    sp.write(chr(0))
    time.sleep(2)
    for i in range(1, (num+1), 1):
        time.sleep(dela)
        out=chr(i) + "\x04\x00\x00\x00\x02"
        crccode = crc16(out)
        ser.write(out + chr(crccode&0xff) + chr(crccode>>8))
        ret1 = ser.read(9)
        print((out + chr(crccode&0xff) + chr(crccode>>8)).encode('hex'))
        if not ret1 or len(ret1) != 9:
            print("incorrect: " + ret1)
            continue
        data = crc16(ret1[0:7])
        crc = ord(ret1[8]) * 256 + ord(ret1[7])
        if data == crc:
	    print("temperature: " + str(float(int(ret1.encode('hex')[6:10], 16))/10))
	    print("humidity: " + str(float(int(ret1.encode('hex')[10:14], 16))/10))
            temper = float(int(ret1.encode('hex')[6:10], 16))/10
			humi = float(int(ret1.encode('hex')[10:14], 16))/10
            jX = clf.predict([[temper, humi]])
			print jX
			if jX==1:
				print("on")
				sp.write(chr(1))
				time.sleep(5)
			else:
				print("off")
				sp.write(chr(0))
				time.sleep(5)
        else:
            print("incorrect: " + ret1.encode('hex'))

exit()
