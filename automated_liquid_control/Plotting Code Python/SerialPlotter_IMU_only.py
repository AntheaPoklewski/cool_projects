import serial 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolours
import matplotlib.animation as animation
from datetime import datetime
from collections import deque
import openpyxl
import time

rawDataSTM = []

thetaData = []
phiData = []

phiData_IMU1 = []
thetaData_IMU1 = []

phiData_IMU2 = []
thetaData_IMU2 = []

STM_port = "COM10" # STM
#ArduinoNano_port = "COM9"

baudrate = 115200
serSTM = serial.Serial(STM_port, baudrate)

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a filename with date and time
filename = f"Data_{current_datetime}.xlsx"

# Open or create an Excel workbook
workbook = openpyxl.Workbook()

# Create a new sheet in the workbook
sheet = workbook.active
sheet.title = "IMU Data Input and Output"

# Write headers
headers = ["Roll IMU1", "Pitch IMU1", "Roll IMU2", "Pitch IMU2"]
sheet.append(headers)

counter = 1
serSTM.flush()

while True:  # while there is a byte waiting 
        try:
            # if serSTM.inWaiting(): # there is data yay
            dataS = serSTM.readline()  
            print("STM = " + str(dataS))

            data_STM_sensor = dataS.decode('utf-8') # it gets transmitted as a string via serial
            STM_data = data_STM_sensor.strip().split(',')

            phiData_IMU1.append(float(STM_data[0]))
            thetaData_IMU1.append(float(STM_data[1]))
            phiData_IMU2.append(float(STM_data[2]))
            thetaData_IMU2.append(float(STM_data[3]))

            # Append all data to sheet
            sheet.append([float(STM_data[0]), float(STM_data[1]), float(STM_data[2]), float(STM_data[3])])  

            counter += 1

            if counter == 2003: # div by 3
                break
            
        except:
          pass

# Plot Things ----------------------------------------------------------------------------------
fig, axs = plt.subplots(2, 1, sharex=True)

axs[0].set_title("Orientation Estimation IMU1 Cup")
axs[0].set_xlabel("Sample")
axs[0].set_ylabel("Orientation (degrees)")
axs[0].plot(phiData_IMU1, 'deeppink', label = "Phi_roll_y")
axs[0].plot(thetaData_IMU1, 'darkorange', label = "Theta_pitch_x")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[0].set_ylim((-30, 30))
axs[0].legend(loc='upper right')
axs[0].grid(True)

axs[1].set_title("Orientation Estimation IMU2 Car")
axs[1].set_xlabel("Sample")
axs[1].set_ylabel("Orientation (degrees)")
axs[1].plot(phiData_IMU2, 'blue', label = "Phi_roll_y")
axs[1].plot(thetaData_IMU2, 'green', label = "Theta_pitch_x")
# plt.plot(psiData, 'g', label = "Psi_yaw_z")
axs[1].set_ylim((-30, 30))
axs[1].legend(loc='upper right')
axs[1].grid(True)

plt.show()
workbook.save("C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/STM Things/SID/" + filename)

serSTM.close()