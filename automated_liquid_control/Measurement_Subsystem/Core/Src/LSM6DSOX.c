
// First IMU used in car for measurements of system
#include <LSM6DSOX.h>
#include <main.h>
#include <stdio.h>
#include <math.h>

extern I2C_HandleTypeDef hi2c1;
// extern I2C_HandleTypeDef hi2c2; <- second channel not needed - SCL -> PB10, SDA -> PB11
// both I2Cs are on the same channel now :p
// IMU1 at memory address IMU1 -> SD0 pin GND
// IMU2 at memory address IMU2 -> SD0 pin VCC
extern UART_HandleTypeDef huart3;

#define PI 3.141592654

// Cup Accel
void InitAccel_IMU1(){ // SCL -> PB8, SDA -> PB9 for both IMUs
	  // Wait until IMU is ready
//	  __HAL_RCC_I2C2_FORCE_RESET();
//	  __HAL_RCC_I2C2_RELEASE_RESET();
	  HAL_Delay(10);
	  HAL_StatusTypeDef ret_dev_ready = HAL_I2C_IsDeviceReady(&hi2c1, IMU1_ADDRESS, 2, HAL_MAX_DELAY);
	  if (ret_dev_ready == HAL_OK){
		  //printf("The device is ready \n");
		  // set up accelerometer configurations
		  uint8_t temp_acc = TEMP_ACC;
		  HAL_StatusTypeDef ret_mem_config = HAL_I2C_Mem_Write(&hi2c1, IMU1_ADDRESS, INT1_CTRL, 1, &temp_acc, 1, HAL_MAX_DELAY);
		  if (ret_mem_config == HAL_OK){
			  //printf("Accel is configured \n");
			  // set up
			  uint8_t acc_config = ACCEL_CFG;
			  HAL_StatusTypeDef ret_accel_ctrl = HAL_I2C_Mem_Write(&hi2c1, IMU1_ADDRESS, CTRL1_XL, 1, &acc_config, 1, HAL_MAX_DELAY);
			  if(ret_accel_ctrl == HAL_OK){
				  //printf("Accel_ctrl has been transmitted \n");
			  }
			  else{
				  //printf("Accel_ctrl has not been transmitted \n");
			  }
		  }
		  else{
			  //printf("Accel is not configured \n");
		  }
	  }
	  else {
		  //printf("The device is not ready \n");
		  Error_Handler();
	  }
}

// Car Accel
void InitAccel_IMU2(){
	  // Wait until IMU is ready
 	  HAL_Delay(10);
	  HAL_StatusTypeDef ret_dev_ready = HAL_I2C_IsDeviceReady(&hi2c1, IMU2_ADDRESS, 2, HAL_MAX_DELAY);
	  if (ret_dev_ready == HAL_OK){
		  //printf("The device is ready \n");
		  // set up accelerometer configurations
		  uint8_t temp_acc = TEMP_ACC;
		  HAL_StatusTypeDef ret_mem_config = HAL_I2C_Mem_Write(&hi2c1, IMU2_ADDRESS, INT1_CTRL, 1, &temp_acc, 1, HAL_MAX_DELAY);
		  if (ret_mem_config == HAL_OK){
			  //printf("Accel is configured \n");
			  // set up
			  uint8_t acc_config = ACCEL_CFG;
			  HAL_StatusTypeDef ret_accel_ctrl = HAL_I2C_Mem_Write(&hi2c1, IMU2_ADDRESS, CTRL1_XL, 1, &acc_config, 1, HAL_MAX_DELAY);
			  if(ret_accel_ctrl == HAL_OK){
				  //printf("Accel_ctrl has been transmitted \n");
			  }
			  else{
				  //printf("Accel_ctrl has not been transmitted \n");
			  }
		  }
		  else{
			  //printf("Accel is not configured \n");
		  }
	  }
	  else {
		  //printf("The device is not ready \n");
		  Error_Handler();
	  }
}

// Cup Gyro
void InitGyro_IMU1(){
	  // Wait until IMU is ready
	  HAL_Delay(10);
	  HAL_StatusTypeDef ret_dev_ready = HAL_I2C_IsDeviceReady(&hi2c1, IMU1_ADDRESS, 2, HAL_MAX_DELAY);
	  if (ret_dev_ready == HAL_OK){
		  //printf("The device is ready \n");
		  // set up accelerometer configuration
		  uint8_t temp_gyro = TEMP_GYRO; // continuous interrupts on INT1 pin -> full flag interrupt
		  HAL_StatusTypeDef ret_mem_config = HAL_I2C_Mem_Write(&hi2c1, IMU1_ADDRESS, INT2_CTRL, 1, &temp_gyro, 1, HAL_MAX_DELAY);
		  if (ret_mem_config == HAL_OK){
			  //printf("Gyro is configured \n");
			  // set up
			  uint8_t gyro_config = GYRO_CFG;
			  HAL_StatusTypeDef ret_gyro_ctrl = HAL_I2C_Mem_Write(&hi2c1, IMU1_ADDRESS, CTRL2_G, 1, &gyro_config, 1, HAL_MAX_DELAY);
			  if(ret_gyro_ctrl == HAL_OK){
				  //printf("Gyro_ctrl has been transmitted \n");
			  }
			  else{
				  //printf("Gyro_ctrl has not been transmitted \n");
			  }
		  }
		  else{
			  //printf("Gyro is not configured \n");
		  }
	  }
	  else {
		  //printf("The device is not ready \n");
		  Error_Handler();
	  }
}

// Car Gyro
void InitGyro_IMU2(){
	  // Wait until IMU is ready
	  HAL_Delay(10);
	  HAL_StatusTypeDef ret_dev_ready = HAL_I2C_IsDeviceReady(&hi2c1, IMU2_ADDRESS, 2, HAL_MAX_DELAY);
	  if (ret_dev_ready == HAL_OK){
		  //printf("The device is ready \n");
		  // set up accelerometer configuration
		  uint8_t temp_gyro = TEMP_GYRO; // continuous interrupts on INT1 pin -> full flag interrupt
		  HAL_StatusTypeDef ret_mem_config = HAL_I2C_Mem_Write(&hi2c1, IMU2_ADDRESS, INT2_CTRL, 1, &temp_gyro, 1, HAL_MAX_DELAY);
		  if (ret_mem_config == HAL_OK){
			  //printf("Gyro is configured \n");
			  // set up
			  uint8_t gyro_config = GYRO_CFG;
			  HAL_StatusTypeDef ret_gyro_ctrl = HAL_I2C_Mem_Write(&hi2c1, IMU2_ADDRESS, CTRL2_G, 1, &gyro_config, 1, HAL_MAX_DELAY);
			  if(ret_gyro_ctrl == HAL_OK){
				  //printf("Gyro_ctrl has been transmitted \n");
			  }
			  else{
				  //printf("Gyro_ctrl has not been transmitted \n");
			  }
		  }
		  else{
			  //printf("Gyro is not configured \n");
		  }
	  }
	  else {
		  //printf("The device is not ready \n");
		  Error_Handler();
	  }
}

const float acc_scaling = 0.061; // +- 2g <- mg/LSB
const float gyro_scaling = 4.375; // <- 125 dps // 8.75; // 250 dps <- mdps/LSB

uint8_t acc_data[6];
uint8_t gyro_data[6];

int16_t x_acc_L;
int16_t y_acc_L;
int16_t z_acc_L;

int16_t x_gyro_L;
int16_t y_gyro_L;
int16_t z_gyro_L;

float x_acc_d;
float y_acc_d;
float z_acc_d;

float x_gyro_d;
float y_gyro_d;
float z_gyro_d;

void LSM6DSOX_readIMU1(float* arr){
	// Poll status register first
	uint8_t check_poll = 0;
	HAL_I2C_Mem_Read(&hi2c1, IMU1_ADDRESS, STATUS_REG, 1, &check_poll, 1, HAL_MAX_DELAY);
	// Accelerometer
	if (check_poll == 0b00000001 || check_poll == 0b00000101 || check_poll == 0b00000111){ // get accel data
		HAL_I2C_Mem_Read(&hi2c1, IMU1_ADDRESS, OUTX_L_A, 1, acc_data, 6, HAL_MAX_DELAY);
		x_acc_L = (int16_t)((acc_data[1] << 8) | acc_data[0]); // twos complement
		x_acc_d = (float)x_acc_L*acc_scaling/1000; // g
		//printf("x-axis acceleration: %d \n", (int)x_acc_d);

		y_acc_L = (int16_t)((acc_data[3] << 8) | acc_data[2]); // twos complement
		y_acc_d = (float)y_acc_L*acc_scaling/1000; // g
		//printf("y-axis acceleration: %d \n", (int)y_acc_d);

		z_acc_L = (int16_t)((acc_data[5] << 8) | acc_data[4]); // twos complement
		z_acc_d = (float)z_acc_L*acc_scaling/1000; // g
		//printf("z-axis acceleration: %d \n", (int)z_acc_d);
	}
	// Gyroscope
	if (check_poll == 0b00000010 || check_poll == 0b00000110 || check_poll == 0b00000111){ // get gyro data
		HAL_I2C_Mem_Read(&hi2c1, IMU1_ADDRESS, OUTX_L_G, 1, gyro_data, 6, HAL_MAX_DELAY);
		x_gyro_L = (int16_t)((gyro_data[1] << 8) | gyro_data[0]); // twos complement
		x_gyro_d = (float)x_gyro_L*gyro_scaling/1000; // dps
		//printf("x-axis acceleration: %d \n", (int)x_gyro_d);

		y_gyro_L = (int16_t)((gyro_data[3] << 8) | gyro_data[2]); // twos complement
		y_gyro_d = (float)y_gyro_L*gyro_scaling/1000; // dps
		//printf("y-axis acceleration: %d \n", (int)y_acc_d);

		z_gyro_L = (int16_t)((gyro_data[5] << 8) | gyro_data[4]); // twos complement
		z_gyro_d = (float)z_gyro_L*gyro_scaling/1000; // dps
		//printf("z-axis acceleration: %d \n", (int)z_gyro_d);
	}

	arr[0] = x_acc_d;
	arr[1] = y_acc_d;
	arr[2] = z_acc_d;
	arr[3] = x_gyro_d;
	arr[4] = y_gyro_d;
	arr[5] = z_gyro_d;
}

void LSM6DSOX_readIMU2(float* arr){
	// Poll status register first
	uint8_t check_poll = 0;
	HAL_I2C_Mem_Read(&hi2c1, IMU2_ADDRESS, STATUS_REG, 1, &check_poll, 1, HAL_MAX_DELAY);
	// Accelerometer
	if (check_poll == 0b00000001 || check_poll == 0b00000101 || check_poll == 0b00000111){ // get accel data
		HAL_I2C_Mem_Read(&hi2c1, IMU2_ADDRESS, OUTX_L_A, 1, acc_data, 6, HAL_MAX_DELAY);
		x_acc_L = (int16_t)((acc_data[1] << 8) | acc_data[0]); // twos complement
		x_acc_d = (float)x_acc_L*acc_scaling/1000; // g
		//printf("x-axis acceleration: %d \n", (int)x_acc_d);

		y_acc_L = (int16_t)((acc_data[3] << 8) | acc_data[2]); // twos complement
		y_acc_d = (float)y_acc_L*acc_scaling/1000; // g
		//printf("y-axis acceleration: %d \n", (int)y_acc_d);

		z_acc_L = (int16_t)((acc_data[5] << 8) | acc_data[4]); // twos complement
		z_acc_d = (float)z_acc_L*acc_scaling/1000; // g
		//printf("z-axis acceleration: %d \n", (int)z_acc_d);
	}
	// Gyroscope
	if (check_poll == 0b00000010 || check_poll == 0b00000110 || check_poll == 0b00000111){ // get gyro data
		HAL_I2C_Mem_Read(&hi2c1, IMU2_ADDRESS, OUTX_L_G, 1, gyro_data, 6, HAL_MAX_DELAY);
		x_gyro_L = (int16_t)((gyro_data[1] << 8) | gyro_data[0]); // twos complement
		x_gyro_d = (float)x_gyro_L*gyro_scaling/1000; // dps
		//printf("x-axis acceleration: %d \n", (int)x_gyro_d);

		y_gyro_L = (int16_t)((gyro_data[3] << 8) | gyro_data[2]); // twos complement
		y_gyro_d = (float)y_gyro_L*gyro_scaling/1000; // dps
		//printf("y-axis acceleration: %d \n", (int)y_acc_d);

		z_gyro_L = (int16_t)((gyro_data[5] << 8) | gyro_data[4]); // twos complement
		z_gyro_d = (float)z_gyro_L*gyro_scaling/1000; // dps
		//printf("z-axis acceleration: %d \n", (int)z_gyro_d);
	}

	arr[0] = x_acc_d;
	arr[1] = y_acc_d;
	arr[2] = z_acc_d;
	arr[3] = x_gyro_d;
	arr[4] = y_gyro_d;
	arr[5] = z_gyro_d;
}

