import serial 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolours
import matplotlib.animation as animation
from datetime import datetime
from collections import deque
import numpy as np
from numpy import savetxt
import pandas as pd
import os
import openpyxl
import time
import xlwt
from tempfile import TemporaryFile

rawDataSTM = []
attitudeArduino = []

thetaData = []
phiData = []
psiData = []

motorAngle1 = []
motorAngle2 = []
motorAngle3 = []

STM_port = "COM10" # STM
ArduinoNano_port = "COM5" # Arduino Motion Shield
ArduinoUno_port = "COM7"
ESP_port = "COM12"

baudrate = 115200
serSTM = serial.Serial(STM_port, baudrate)
serArduino = serial.Serial(ArduinoNano_port, baudrate)
serUno = serial.Serial(ArduinoUno_port, baudrate)
serESP = serial.Serial(ESP_port, baudrate)

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a filename with date and time
filename = f"Data_{current_datetime}.xlsx"

# Open or create an Excel workbook
workbook = openpyxl.Workbook()

# Create a new sheet in the workbook
sheet = workbook.active
sheet.title = "IMU Data"

# Write headers
headers = ["Motor1", "Motor2", "Motor3" "Roll", "Pitch"]
sheet.append(headers)

SamplingPeriod = 10
counter = 1
flag = False

serArduino.flush()
serSTM.flush()

while True:  # while there is a byte waiting 
        try:
            if serSTM.inWaiting(): # there is data yay
                flag = True
                serArduino.flush()
                serSTM.flush()

            if flag == True:
                serArduino.flush()
                serSTM.flush()
                dataS = serSTM.readline()  
                
                dataA = serArduino.readline() # only read data if STM is reading data # Motor1
                dataUno = serUno.readline() # Motor2
                dataESP = serESP.readline() # Motor3
                
                # print("STM = " + str(dataS))
                # print("Arduino = " + str(dataA))

                data_STM_sensor = dataS.decode('utf-8') # it gets transmitted as a string via serial
                STM_data = data_STM_sensor.strip().split(',')

                # Motor 1
                data_Arduino_sensor = dataA.decode('utf-8') # it gets transmitted as a string via serial
                Arduino_data = data_Arduino_sensor.strip().split(',')

                # Motor 2
                data_Uno_sensor = dataUno.decode('utf-8') # it gets transmitted as a string via serial
                Uno_data = data_Uno_sensor.strip().split(',')

                # Motor 3
                data_ESP_sensor = dataESP.decode('utf-8') # it gets transmitted as a string via serial
                ESP_data = data_ESP_sensor.strip().split(',')

                phiData.append(float(STM_data[0]))
                thetaData.append(float(STM_data[1]))
                psiData.append(float(STM_data[2]))

                motorAngle1.append(float(Arduino_data[0]))
                motorAngle2.append(float(Uno_data[0]))
                motorAngle3.append(float(ESP_data[0]))

                # Append all data to sheet
                sheet.append([float(Arduino_data[0]), float(Uno_data[0]), float(ESP_data[0]), float(STM_data[0]), float(STM_data[1])])  

                counter += 1

                if counter == 2003: # div by 3 -> 1000 samples 
                    break
            
        except:
          pass


# print("Motor Angle")
# for i in range(0, len(motorAngle)):
#     print(motorAngle[i])

# print("Roll")
# for i in range(0, len(phiData)):
#     print(phiData[i])

# print("Pitch")
# for i in range(0, len(thetaData)):
#     print(thetaData[i])

# Plot Things ----------------------------------------------------------------------------------
fig, axs = plt.subplots(4, 1, sharex=True)

axs[0].set_title("Magdwick Orientation Estimation Output")
axs[0].set_xlabel("Sample")
axs[0].set_ylabel("Roll/Pitch Orientation (degrees)")
axs[0].plot(phiData, 'deeppink', label = "Phi_roll_y")
axs[0].plot(thetaData, 'darkorange', label = "Theta_pitch_x")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[0].set_ylim((-90, 90))
axs[0].legend(loc='upper right')
axs[0].grid(True)

axs[1].set_title("Servo Motor1 Input Angle")
axs[1].set_xlabel("Sample")
axs[1].set_ylabel("Rotation Angle (Degrees)")
axs[1].plot(motorAngle1, 'blue', label = "Angle")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[1].set_ylim((-90, 90))
axs[1].legend(loc='upper right')
axs[1].grid(True)

axs[2].set_title("Servo Motor2 Input Angle")
axs[2].set_xlabel("Sample")
axs[2].set_ylabel("Rotation Angle (Degrees)")
axs[2].plot(motorAngle2, 'blue', label = "Angle")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[2].set_ylim((-90, 90))
axs[2].legend(loc='upper right')
axs[2].grid(True)

axs[3].set_title("Servo Motor3 Input Angle")
axs[3].set_xlabel("Sample")
axs[3].set_ylabel("Rotation Angle (Degrees)")
axs[3].plot(motorAngle3, 'blue', label = "Angle")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[3].set_ylim((-90, 90))
axs[3].legend(loc='upper right')
axs[3].grid(True)

plt.show()
workbook.save("C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/STM Things/SID/" + filename)

serSTM.close()
serArduino.close()