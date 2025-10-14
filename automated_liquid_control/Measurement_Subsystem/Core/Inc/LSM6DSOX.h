
#ifndef INC_LSM6DSOX_H_
#define INC_LSM6DSOX_H_

// Variables
#define IMU1_ADDRESS 0X6A << 1 //  control register device <- 1101010 <- cup
#define IMU2_ADDRESS 0X6B << 1 // <- 1101011 <- car
#define STATUS_REG 0x1E // check if data available

// Accelerometer vals
#define CTRL1_XL 0x10
#define ACCEL_CFG 0b01100000 // 416 Hz, +- 2g // 0b01000000 <- 104 Hz
#define INT1_CTRL 0x0D // enables signal to be carried over INT1
#define TEMP_ACC 0b00000001  // continuous interrupts on INT1 pin -> full flag interrupt

#define OUTX_L_A 0x28 // Hexadecimal address for the DATAX0 internal register.
#define OUTX_H_A 0x29 // Hexadecimal address for the DATAX1 internal register.
#define OUTY_L_A 0x2A
#define OUTY_H_A 0x2B
#define OUTZ_L_A 0x2C
#define OUTZ_H_A 0x2D

// Gyroscope vals
#define CTRL2_G 0x11
#define GYRO_CFG 0b01100001 // 416 Hz, +- 125 dps // 0b01000000 <- 104 Hz
#define INT2_CTRL 0x0E
#define TEMP_GYRO 0b00000010

#define OUTX_L_G 0x22
#define OUTX_H_G 0x23 // Hexadecimal address for the DATAX1 internal register.
#define OUTY_L_G 0x24
#define OUTY_H_G 0x25
#define OUTZ_L_G 0x26
#define OUTZ_H_G 0x27

void InitAccel_IMU1();
void InitAccel_IMU2();
void InitGyro_IMU1();
void InitGyro_IMU2();
void LSM6DSOX_readIMU1();
void LSM6DSOX_readIMU2();

#endif /* INC_LSM6DSOX_H_ */
