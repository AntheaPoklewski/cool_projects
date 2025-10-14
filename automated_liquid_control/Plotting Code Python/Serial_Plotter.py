import serial 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolours
import matplotlib.animation as animation
from datetime import datetime
from collections import deque
import openpyxl
import time

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a filename with date and time
filename = f"Spec2_New{current_datetime}.xlsx"

# Open or create an Excel workbook
workbook = openpyxl.Workbook()

# Create a new sheet in the workbook
sheet = workbook.active
sheet.title = "Spec_ManualAdj_Data"

# Write headers
headers = ["STM_roll", "STM_pitch", "Arduino_roll", "Arduino_pitch"]
sheet.append(headers)

rawDataSTM = []
attitudeArduino = []

theta_pitch_cup = []
phi_roll_cup = []
psiData = []

# pitch_BN055 = [0]*550
# roll_BN055 = [0]*550
# yawList = []

# extra_Arr = [0]*550

pitch_BN055 = [0]
roll_BN055 = [0]
yawList = []

extra_Arr = [0]

STM_port = "COM10" # STM
platform_port = "COM3" # Arduino Motion Shield

baudrate = 115200
serSTM = serial.Serial(STM_port, baudrate)
serArduino = serial.Serial(platform_port, baudrate)

SamplingPeriod = 10
counter = 1
counterArduino = 0
flag = False

timestamps1 = []
timestamps2 = []

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
                dataA = serArduino.readline() # only read data if STM is reading data
                
                print("STM = " + str(dataS))
                print("Arduino = " + str(dataA))

                data_STM_sensor = dataS.decode('utf-8') # it gets transmitted as a string via serial
                STM_data = data_STM_sensor.strip().split(',')

                data_Arduino_sensor = dataA.decode('utf-8') # it gets transmitted as a string via serial
                Arduino_data = data_Arduino_sensor.strip().split(',')

                timestamps1.append(time.time())
                phi_roll_cup.append(float(STM_data[0]))
                theta_pitch_cup.append(float(STM_data[1]))

                # if counterArduino < 4450:
                #     yawList.append(float(Arduino_data[0]))
                #     roll_BN055.append(float(Arduino_data[2]))
                #     pitch_BN055.append(float(Arduino_data[1])) 

                # print(STM_data[0])
                # print(float(STM_data[1]))

                yawList.append(float(Arduino_data[0]))
                roll_BN055.append(float(Arduino_data[2]))
                pitch_BN055.append(float(Arduino_data[1])) 

                counter += 1

                if counter == 3000: # div by 3
                    break
            
        except:
          pass
# for i in range(0, len(extra_Arr) - 1):
#     phi_roll_cup.append(extra_Arr[i])
#     theta_pitch_cup.append(extra_Arr[i])


for i in range(0, len(theta_pitch_cup)):
    sheet.append([phi_roll_cup[i], theta_pitch_cup[i], roll_BN055[i], pitch_BN055[i]])
                
# i = 0
# while i <= (len(rawDataSTM)-3): # Populate arrays
#      phiData.append(rawDataSTM[i]) # y STM
#      yawList.append(attitudeArduino[i]) # z Arduino

#      thetaData.append(rawDataSTM[i+1]) # x STM
#      pitchList.append(attitudeArduino[i+1]) # x Arduino

#      psiData.append(rawDataSTM[i+2]) # z STM
#      rollList.append(attitudeArduino[i+2]) # y Arduino

#      i += 3

# print(len(thetaData))
# print(len(phiData))
# print(len(psiData))

# Plot Things ----------------------------------------------------------------------------------
fig, axs = plt.subplots(2, 1, sharex=True)
# plt.rcParams['font.family'] = 'Times New Roman'

axs[0].set_title("Orientation Estimation")
axs[0].set_xlabel("Sample")
axs[0].set_ylabel("Orientation (degrees)")
axs[0].plot(phi_roll_cup, 'deeppink', label = "Phi_roll STM")
axs[0].plot(roll_BN055 , 'darkorange', label = "Phi_roll BNO55")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[0].set_ylim((-90, 90))
axs[0].legend(loc='upper right')
axs[0].grid(True)

axs[1].set_title("BNO55 Module Orientation Estimation")
axs[1].set_xlabel("Sample")
axs[1].set_ylabel("Orientation (degrees)")
axs[1].plot(theta_pitch_cup, 'b', label = "Theta_pitch_x STM32")
axs[1].plot(pitch_BN055, 'g', label = "Theta_pitch_x BNO55")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[1].set_ylim((-90, 90))
axs[1].legend(loc='upper right')
axs[1].grid(True)

plt.show()
workbook.save("C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Results/" + filename)

serSTM.close()
serArduino.close()