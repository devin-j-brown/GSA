import serial
import time
import math
import numpy as np
import csv
from Quat_Funcs import quat_to_euler
from Csv_Manip import trim_csv

from pyquaternion import Quaternion

# Make sure to change the usb device accordingly
arduinoData = serial.Serial("/dev/ttyUSB0", 115200)

seconds_to_record = 10
in_file_name = "all_data.csv"
out_file_name = "all_data_trimmed.csv"

time.sleep(1)


def get_sensor_data(seconds_to_record, in_file_name, out_file_name):

    # Sets t_end based on current clock time
    t_end = time.time() + seconds_to_record

    # Redeclaring the file name to clear out previous swing
    f = open(in_file_name, "w+")
    f.close()

    # Runs while loop for desired duration
    while time.time() < t_end:

        # Waiting on the sensor to detect new data
        while arduinoData.inWaiting() == 0:
            pass

        # Reading serial data from the sensor and parsing it
        # Channels 0-3:  Calibration accel, gyro, magnetometer, system
        # Channels 4-7:  Quaternion w, x, y, z
        # Channels 8-10: linear acceleration
        # Channel  11:   time since program start in ms
        dataPacket = arduinoData.readline()
        dataPacket = str(dataPacket, "utf-8")
        splitPacket = dataPacket.split(",")
        splitPacketFloat = [float(item) for item in splitPacket]
        calibration_data = splitPacketFloat[0:4]
        q = splitPacketFloat[4:8]

        # Calculating pitch, roll, and yaw and appending them to the packet
        pitch, roll, yaw = quat_to_euler(q[0], q[1], q[2], q[3])
        splitPacketFloat.extend([pitch, roll, yaw])

        # Printing pitch, roll, and yaw for troubleshooting purposes
        print(f"pitch = {pitch}, roll = {roll}, yaw = {yaw}")

        # Writing each line of data to the csv
        with open(in_file_name, mode="a") as euler_angles:
            euler_writer = csv.writer(euler_angles, delimiter=",")
            euler_writer.writerow(splitPacketFloat)

    trim_csv(in_file_name, out_file_name)


get_sensor_data(seconds_to_record, in_file_name, out_file_name)
