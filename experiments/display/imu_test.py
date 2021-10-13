import os
import sys
import time
import smbus

from imusensor.MPU9250 import MPU9250

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()
# imu.caliberateGyro()
# imu.caliberateAccelerometer()
# or load your own caliberation file
# imu.loadCalibDataFromFile("/home/pi/calib_real_bolder.json")

# imu.caliberateMagApprox()
imu.caliberateGyro()

yaw = 0
start = time.time()
while True:
    dt = time.time() - start
    imu.readSensor()
    yaw += imu.GyroVals[2]*dt*100
    print(yaw)
    start = time.time()