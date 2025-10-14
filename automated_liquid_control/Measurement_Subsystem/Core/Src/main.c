/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <string.h>
#include <stdio.h>
#include "LSM6DSOX.h" // for accelerometer and gyroscope sensor 0 -> on car
#include <math.h>
#include <stdlib.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
#define PI 3.141592654
#define g 9.807
float deg_to_rad = PI/180;
float rad_to_deg = 180/PI;

// Timer delays --------------------------------------------------------------
uint32_t PWM_counter = 0; // Timer 16
uint32_t prev_timer_val = 0; // Timer 17
uint32_t curr_timer_val = 0;
uint32_t timer_diff = 0;

// IMU variables -------------------------------------------------------------
float vals[6] = {0}; // IMU_1
float x_accIMU1 = 0;
float y_accIMU1 = 0;
float z_accIMU1 = 0;
float x_gyroIMU1 = 0;
float y_gyroIMU1 = 0;
float z_gyroIMU1 = 0;

float x_accIMU2 = 0;
float y_accIMU2 = 0;
float z_accIMU2 = 0;
float x_gyroIMU2 = 0;
float y_gyroIMU2 = 0;
float z_gyroIMU2 = 0;

// Filter variables ------------------------------------------------------------
// Initialization Magdwick
const float constantBiasRoll = 0; //1.0640; // deg/s
const float constantBiasPitch = 0; //0.8084; // deg/s
const float constantBiasYaw = 0; //1.1199; // deg/s

//float beta = 0.8660*(0.1)*(PI/180);  // <- maximum gyro error around 1 degree
const float beta = 0.5; //0.041; //0.164;
const float gravity = -9.807;

const float alpha = 0.96;
float prev_IMU1[3] = {0, 0, 0};
float prev_IMU2[3] = {0, 0, 0};

float theta_xIMU1 = 0;
float phi_yIMU1 = 0;
float psi_zIMU1 = 0;

float theta_xIMU2 = 0;
float phi_yIMU2 = 0;
float psi_zIMU2 = 0;

// Arrays
float A[3] = {0, 0, 0}; // Acceleration
float G[4] = {0, 0, 0, 0}; // Gyroscope
float Q[4] = {1, 0, 0, 0};

float attitude[3] = {0, 0, 0};
float F[3] = {0, 0, 0};
float J_1[3] = {0, 0, 0};
float J_2[3] = {0, 0, 0};
float J_3[3] = {0, 0, 0};
float J_4[3] = {0, 0, 0};
float step[4] = {0, 0, 0, 0};

float Q_int[4] = {0, 0, 0, 0}; // New Quaternion after integration
float qDot[4] = {0, 0, 0, 0}; // Multiplied
float car_forces[3] = {0, 0, 0};

volatile float car_roll_ySP = 0;
volatile float car_pitch_xSP = 0;
volatile float cup_roll_ySP = 0;
volatile float cup_pitch_xSP = 0;

float x_force = 0;
float y_force = 0;
float z_force = 0;

float car_pitch_xSP_copy = 0;
float car_roll_ySP_copy = 0;
float cup_pitch_xSP_copy = 0;
float cup_roll_ySP_copy = 0;

float cup_x_response = 0.0;
float cup_y_response = 0.0;

int flag_v1 = 0; // check if first round values are in yet

// PID variables -------------------------------------------------------------
float error_prev[2] = {0, 0};
float error[2] = {0, 0};
float integral[2] = {0, 0};
float derivative[2] = {0, 0};
float PID_output[2] = {0, 0};
float PID_output_prev[2] = {0, 0};
float alpha_f[2] = {0.18, 0.18}; // 0 <= a <= 1

// Adaptive PID ----------------------------------------------------------------
float prev_xSP = 0;
float prev_ySP = 0;
float delta_x = 0;
float delta_y = 0;

float KP_mid[2] = {5, 10}; // for alpha = 2.5
float KI_mid[2] = {0.7, 0.6};
float KD_mid[2] = {0.07, 0.08};

float KP[2] = {5, 5}; // for alpha = 2.5
float KI[2] = {0.5, 0.5};
float KD[2] = {0.05, 0.05};

// PP Controlller -------------------------------------------
float pitch_x_curr = 0.0;  // n_current = (0, 0, h) -> initial normal of system
float roll_y_curr = 0.0;
float alpha_PP[2] = {0.2, 0.2}; // 0 <= a <= 1
float PP[2] = {0, 0};
float K[2] = {-422.8500, 2.8640};
float Kdc = 0.5;

// Inverse Kinematics --------------------------------------------------------
const float r = 9; // cm -> rad plate = rad base
const float h = 13.2;
const float L1 = 15;
const float L2 = 7;

float A_p[3] = {0, 0, 0};
float B_p[3] = {0, 0, 0};
float C_p[3] = {0, 0, 0};

float A_r[3] = {0, 0, 0};
float B_r[3] = {0, 0, 0};
float C_r[3] = {0, 0, 0};

float A_mid = 0;
float B_mid = 0;
float C_mid = 0;
float D_mid = 0;
float E_mid = 0;
float angle = 0;

// Calculate norm -------------------------------------------------------------
float n_body[3] = {0, 0, 0};
float global[3] = {0, 0, 13.2}; // origin of plate
float n_m1[3] = {0, 0, 0};
float n_m2[3] = {0, 0, 0};
float n_m3[3] = {0, 0, 0};

int pitch_flag = 0; // for +ve and -ve pitch rotations
int roll_flag = 0; // for +ve and -ve roll rotations

// Actuate Motors ------------------------------------------------------------
float motorAngle[3] = {0, 0, 0};
float currentAngle[3] = {30, 30, 30}; // motors start at 25 degrees for initial position
float angleKin[3] = {0, 0, 0};
int PWMangle[3] = {2668, 2668, 2668}; //starting at 30 degrees

float angle_start = 30; // starting angle at 30 degrees from -13.729 degrees from horizon
float angle_prev[3] = {30, 30, 30};

// Blutooth module
uint8_t rxData[1];
float txData[6] = {0, 0, 0, 0, 0, 0}; // <- float = 4 bytes x 6 -> 24 bytes
int rxFlag = 0;
float PID_p_tx = 0;
float PID_r_tx = 0;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
#ifdef __GNUC__
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif

PUTCHAR_PROTOTYPE
{
  HAL_UART_Transmit(&huart3, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
  return ch;
}

// My Functions
void CF_IMU1(float, float, float, float, float, float);
void CF_IMU2(float, float, float, float, float, float);
void OrientationEst1(void);
void OrientationEst2(void);
//void Transmit_CF_PC(void);
//void Magdwick(void);
//void Transmit_Mag_PC(void);

void PID(void);
void ActuateMotors(float, float);
float InvKinematics(int, float, float);
int FindPWM(float);
void CalcTime(void);
void GainScheduling(void);
//void PPController(void);

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM2_Init();
  MX_TIM1_Init();
  MX_TIM16_Init();
  MX_TIM17_Init();
  MX_I2C2_Init();
  MX_I2C1_Init();
  MX_USART2_UART_Init();
  MX_USART3_UART_Init();
  /* USER CODE BEGIN 2 */
// Bluetooth module
  HAL_UART_Receive_IT(&huart2, (uint8_t*)rxData, 1); // enable ISR
  HAL_UART_Transmit_IT(&huart2, (uint8_t*)txData, 4*sizeof(txData)); // enabling interrupt transmit

  // IMU modules 1 and 2
  InitAccel_IMU1();
  InitAccel_IMU2();
  InitGyro_IMU1();
  InitGyro_IMU2();

  // Motors
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);

  // Initialise motors to 0
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 1600); // 0 degrees
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 1600); // 0 degrees
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, 1600); // 0 degrees
  HAL_Delay(1000);

  // Initialise motors to 25 degrees if not at 25 already
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 2490); // 25 degrees
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 2490); // 25 degrees
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, 2490); // 25 degrees
  HAL_Delay(1000);

  // Start timers
  HAL_TIM_Base_Start_IT(&htim16); // starts interrupt PWM timer
  HAL_TIM_Base_Start(&htim17); // starts integral counter

// Set PWM for each channel -> set motors all to 25 degrees
  PWM_counter = 0; // set PWMcounter for loop = 0
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */

  while (1)
  {
	  // check if data has been received to start transmission via Blutooth
	  if (rxData[0] == 's'){
		  rxFlag = 1;
	  }
	  if (rxFlag == 1){
		  uint8_t *data = (uint8_t*)&txData;
		  HAL_UART_Transmit_IT(&huart2, data, 6*sizeof(float));
	  }

	  // Atomic block to access ISR variable
	  // Update variables
	  car_pitch_xSP_copy = car_pitch_xSP;
	  car_roll_ySP_copy = car_roll_ySP;
	  x_force = x_accIMU2;
	  y_force = y_accIMU2;
//	  Transmit_CF_PC();

	  car_pitch_xSP_copy = 4*car_pitch_xSP_copy;
	  car_roll_ySP_copy = 4*car_roll_ySP_copy;

	  GainScheduling();
	  PID();
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */

  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Supply configuration update enable
  */
  HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY);

  /** Configure the main internal regulator output voltage
  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

  while(!__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY)) {}

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_DIV1;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 12;
  RCC_OscInitStruct.PLL.PLLP = 2;
  RCC_OscInitStruct.PLL.PLLQ = 2;
  RCC_OscInitStruct.PLL.PLLR = 2;
  RCC_OscInitStruct.PLL.PLLRGE = RCC_PLL1VCIRANGE_3;
  RCC_OscInitStruct.PLL.PLLVCOSEL = RCC_PLL1VCOWIDE;
  RCC_OscInitStruct.PLL.PLLFRACN = 0;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
                              |RCC_CLOCKTYPE_D3PCLK1|RCC_CLOCKTYPE_D1PCLK1;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.SYSCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB3CLKDivider = RCC_APB3_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_APB1_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_APB2_DIV1;
  RCC_ClkInitStruct.APB4CLKDivider = RCC_APB4_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
// Controller code functions --------------------------------------------------------------------
void GainScheduling(){
	delta_x = sqrt(car_pitch_xSP_copy*car_pitch_xSP_copy) - sqrt(prev_xSP*prev_xSP);
	delta_y = sqrt(car_roll_ySP_copy*car_roll_ySP_copy) - sqrt(prev_ySP*prev_ySP);

	delta_x = sqrt(delta_x*delta_x);
	delta_y = sqrt(delta_y*delta_y);
	for (int i = 0; i < 2; i++){
		if(i == 0){
			KP[i] = KP_mid[i];
//			if (delta_x < 2) { // Gain scheduling for bigger errors
//				KP[i] = 0.8*KP_mid[i];
//			}
//			else if ((delta_x >= 2) && (delta_x < 4)){ // Gain scheduling for bigger errors
//				KP[i] = 1.1*KP_mid[i];
//			}
//			else if ((delta_x >= 4) && (delta_x < 6)){ // Gain scheduling for bigger errors
//				KP[i] = 1.3*KP_mid[i];
//			}
//			else if ((delta_x >= 6) && (delta_x < 8)){ // Gain scheduling for bigger errors
//				KP[i] = 1.5*KP_mid[i];
//			}
//			else if ((delta_x >= 8) && (delta_x < 10)){ // Gain scheduling for bigger errors
//				KP[i] = 1.7*KP_mid[i];
//			}
//			else if (delta_x >= 10){
//				KP[i] = 1.9*KP_mid[i];
//			}
		}
		if(i == 1){
			KP[i] = KP_mid[i];

//			if (delta_y < 2) { // Gain scheduling for bigger errors
//				KP[i] = 0.8*KP_mid[i];
//			}
//			else if ((delta_y >= 2) && (delta_y < 4)){ // Gain scheduling for bigger errors
//				KP[i] = 1.1*KP_mid[i];
//			}
//			else if ((delta_y >= 4) && (delta_y < 6)){ // Gain scheduling for bigger errors
//				KP[i] = 1.3*KP_mid[i];
//			}
//			else if ((delta_y >= 6) && (delta_y < 8)){ // Gain scheduling for bigger errors
//				KP[i] = 1.5*KP_mid[i];
//			}
//			else if ((delta_y >= 8) && (delta_y < 10)){ // Gain scheduling for bigger errors
//				KP[i] = 1.7*KP_mid[i];
//			}
//			else if (delta_y>= 10){
//				KP[i] = 1.9*KP_mid[i];
//			}
		}
	}
}


void PID(){
	// Becomes new setpoint for platform // Control system tracks changes roll and pitch
	for (int i = 0; i < 2; i++){
		error_prev[i] = error[i];
		if (i == 0){
			error[i] = car_pitch_xSP_copy - pitch_x_curr; // angle error in x
		}
		if (i == 1){
			error[i] = car_roll_ySP_copy - roll_y_curr; // angle error in y
		}

		if (isnan(error[i])){
			error[i] = 0;
		}

		CalcTime();
		integral[i] += error[i]*((float)timer_diff/10000);
		derivative[i] = (error[i] - error_prev[i])/((float)timer_diff/10000);
		PID_output[i] = KP[i]*error[i] + KI[i]*integral[i] + KD[i]*derivative[i];

		// Account for NAN
		if (isnan(PID_output[i])){
			PID_output[i] = 0;
		}

		// Smoothing filter for motors
		PID_output[i] = (alpha_f[i]*PID_output[i]) + (1.0 - alpha_f[i])*PID_output_prev[i];

		// Update values
		PID_output_prev[i] = PID_output[i];
	}
	PID_p_tx = PID_output[0]; // pitch
	PID_r_tx = PID_output[1];

	// Check if angle error -ve
	if (PID_output[0] < 0){
		PID_output[0] = -PID_output[0]; // make positive
		pitch_flag = 1; // negative error
	}

	if (PID_output[1] < 0){
			PID_output[1] = -PID_output[1]; // make positive
			roll_flag = 1;
	}

	ActuateMotors(PID_output[0], PID_output[1]); // angle setpoint
	// Then need to compare outputs
	// update current position of cup

	cup_pitch_xSP_copy = cup_pitch_xSP;
	cup_roll_ySP_copy = cup_roll_ySP;

//	pitch_x_curr = cup_pitch_xSP_copy;
//	roll_y_curr = cup_roll_ySP_copy;

	// Update PID current values
	pitch_x_curr = car_pitch_xSP_copy;
	roll_y_curr = car_roll_ySP_copy;

	// update FF controller
	prev_xSP = car_pitch_xSP_copy;
	prev_ySP = car_roll_ySP_copy;

	PWM_counter = 0;
}

// Subfunctions of PID ---------------------------------------------------------
void ActuateMotors(float x_angle, float y_angle){
	// Testing
//	x_angle = 30;
//	y_angle = 30;

	// Convert to degrees
	x_angle = x_angle*deg_to_rad;
	y_angle = y_angle*deg_to_rad;

	if (isnan(x_angle)){ // check for error
		x_angle = 0;
	}

	if (isnan(y_angle)){ // check for error
		y_angle = 0;
	}

	// Cap max angles
	if (x_angle > 62){
		x_angle = 62;
	}
	if (y_angle > 65){
		y_angle = 65;
	}

	for(int i = 0; i < 3; i ++){
		angleKin[i] = InvKinematics(i, x_angle, y_angle); // return positive angle
		if (i == 0){ // Motor 1 -> pitch motor (+x, 0)
			if (pitch_flag == 1){ // pitch -ve
				motorAngle[0] = currentAngle[0] + angleKin[0]; // - for control
				pitch_flag = 0; // reset pitch flag
//				currentAngle[0] = motorAngle[0]; // new angle set point
			}
			else { // pitch +ve
				motorAngle[0] = currentAngle[0] - angleKin[0]; // + fr control
//				currentAngle[0] = motorAngle[0];
			}
		}

		if (i == 1){ // Motor 2 -> roll motor (-x, -y)
			if (roll_flag == 1){ // roll -ve
				motorAngle[1] = currentAngle[1] - angleKin[1]; // -> opposite motor 3 // + for control
//				currentAngle[1] = motorAngle[1];
			}
			else { // pitch +ve
				motorAngle[1] = currentAngle[1] + angleKin[1]; // - for control
//				currentAngle[1] = motorAngle[1];
			}
		}

		if (i == 2){ // Motor 3 -> roll motor (-x, +y)
			if (roll_flag == 1){ // roll -ve
				motorAngle[2] = currentAngle[2] + angleKin[2]; // -> opposite motor 2
				roll_flag = 0; // reset roll flag
//				currentAngle[2] = motorAngle[2];
			}
			else { // pitch +ve
				motorAngle[2] = currentAngle[2] - angleKin[2];
//				currentAngle[2] = motorAngle[2];
			}
		}
		// theta[i] = 0.05*motorAngle[i] + 0.95*angle_prev[i]; // cubic equation
		//angle_prev[i] = theta[i];

		PWMangle[i] = FindPWM(motorAngle[i]);
		if (PWMangle[i] < 1650){ // min
			PWMangle[i] = 1650; // make 0
		}

		if (PWMangle[i] > 4626){ // max
			PWMangle[i] = 4626; // make 88
		}
	}

	// Set PWM for each channel
	// computeSpeed -> do accel calcs
	// save starting time

	while (PWM_counter < 9){
		__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, PWMangle[0]); // PE9 -> Motor 1
		__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, PWMangle[1]); // PE11 -> Motor 2
		__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, PWMangle[2]); // PE13 -> Motor 3
	}
}


// starting angle = 30 -> 2668
// maximum angle = 85 -> 4626
// minimum angle = 0 -> 1600
int FindPWM(float angle_in){
	return (int)(1600 + angle_in*35.6); // conversion to PWM with 320 Hz and 180 degree range
}


float InvKinematics(int motor, float theta_pitch, float phi_roll){
	// Calculate inverse kinematics equations here

	// Roll-pitch-roll transform
	// float psi_yaw = 0;
	// body[0] = global[0]*cos(psi_yaw)*cos(theta_pitch) + global[1]*sin(psi_yaw)*cos(theta_pitch) - global[2]*sin(theta_pitch);
	// body[1] = global[1]*(cos(psi_yaw)*sin(theta_pitch)*sin(phi_roll) - sin(psi_yaw)*cos(phi_roll)) + global[1]*(sin(psi_yaw)*sin(theta_pitch)*sin(phi_roll) + cos(psi_yaw)*cos(phi_roll)) + global[2]*cos(theta_pitch)*sin(phi_roll);
	// body[2] = global[2]*(cos(psi_yaw)*sin(theta_pitch)*sin(phi_roll) + sin(psi_yaw)*sin(phi_roll)) + global[1]*(sin(psi_yaw)*sin(theta_pitch)*cos(phi_roll) - cos(psi_yaw)*sin(phi_roll)) + global[2]*cos(theta_pitch)*cos(phi_roll);

	switch(motor){
		case 0:
			// Motor 1 -> pitch
			// Calc norm
			n_m1[0] = global[0]*cos(theta_pitch) - global[2]*sin(theta_pitch);
			n_m1[1] = 0;
			n_m1[2] = global[0]*sin(theta_pitch) + global[2]*cos(theta_pitch);

			// Find leg orientation in space ito x, y, z
			A_p[0] = r*n_m1[2]/sqrt(n_m1[0]*n_m1[0] + n_m1[2]*n_m1[2]);
			A_p[2] = h - (n_m1[0]*r)/sqrt(n_m1[2]*n_m1[2] + n_m1[0]*n_m1[0]);
			A_p[1] = 0;

			// Find orientation of revolute joint between 2 legs in space
			A_mid = (r - A_p[0])/A_p[2];
			B_mid = (A_p[0]*A_p[0] + A_p[2]*A_p[2] + L2*L2 - L1*L1 - r*r)/(2*A_p[2]);
			C_mid = A_mid*A_mid + 1;
			D_mid = 2*(A_mid*B_mid - r);
			E_mid = B_mid*B_mid + r*r - L2*L2;

			A_r[0] = (-D_mid + sqrt(D_mid*D_mid - 4*C_mid*E_mid))/(2*C_mid);
			A_r[1] = 0;
			A_r[2] = sqrt(L2*L2 - A_r[0]*A_r[0] + 2*A_r[0]*r - r*r);

			// Find angle to be rotated by servos
			angle = atan(A_r[2]/(A_r[0]-r))*rad_to_deg;
			if (isnan(angle)){ // check for error
				angle = 90;
			}

			break;

		case 1:
			// Motor 2 -> roll 1
			n_m2[0] = global[0];
			n_m2[1] = global[1]*cos(phi_roll/2) + global[2]*sin(phi_roll);
			n_m2[2] = -global[1]*sin(phi_roll/2) + global[2]*cos(phi_roll);

			B_p[0] = -(r*n_m2[2])/(sqrt(n_m2[0]*n_m2[0] + 3*n_m2[1]*n_m2[1] + 4*n_m2[2]*n_m2[2] + 2*sqrt(3)*n_m2[0]*n_m2[1]));
			B_p[1] = -(sqrt(3)*r*n_m2[2])/(sqrt(n_m2[0]*n_m2[0] + 3*n_m2[1]*n_m2[1] + 4*n_m2[2]*n_m2[2] + 2*sqrt(3)*n_m2[0]*n_m2[1]));
			B_p[2] = h + (r*(sqrt(3)*n_m2[1] + n_m2[0])/(sqrt(n_m2[0]*n_m2[0] + 3*n_m2[1]*n_m2[1] + 4*n_m2[2]*n_m2[2] + 2*sqrt(3)*n_m2[0]*n_m2[1])));

			A_mid = -(B_p[0] + sqrt(3)*B_p[1] + 2*r)/B_p[2];
			B_mid = (B_p[0]*B_p[0] + B_p[1]*B_p[1] + B_p[2]*B_p[2] + L2*L2 - L1*L1 - r*r)/(2*B_p[2]);
			C_mid = A_mid*A_mid + 4;
			D_mid = 2*A_mid*B_mid + 4*r;
			E_mid = B_mid*B_mid - L2*L2 + r*r;

			B_r[0] = (-D_mid - sqrt(D_mid*D_mid - 4*C_mid*E_mid))/(2*C_mid);
			B_r[1] = sqrt(3)*B_r[0];
			B_r[2] = sqrt(L2*L2 - 4*r*B_r[0] - 4*B_r[0]*B_r[0] - r*r);

			angle = atan(B_r[2]/(sqrt(B_r[0]*B_r[0] + B_r[1]*B_r[1]) - r))*rad_to_deg;
			if (isnan(angle)){
				angle = 90;
			}

			angle = angle/2;
			break;

		case 2:
			// Motor 3 -> roll 2
			n_m3[0] = global[0];
			n_m3[1] = global[1]*cos(phi_roll/2) + global[2]*sin(phi_roll);
			n_m3[2] = -global[1]*sin(phi_roll/2) + global[2]*cos(phi_roll);

			C_p[0] = -(r*n_m3[2])/(sqrt(n_m3[0]*n_m3[0] + 3*n_m3[1]*n_m3[1] + 4*n_m3[2]*n_m3[2] - 2*sqrt(3)*n_m3[0]*n_m3[1]));
			C_p[1] = (sqrt(3)*r*n_m3[2])/(sqrt(n_m3[0]*n_m3[0] + 3*n_m3[1]*n_m3[1] + 4*n_m3[2]*n_m3[2] - 2*sqrt(3)*n_m3[0]*n_m3[1]));
			C_p[2] = h - (r*(-sqrt(3)*n_m3[1] + n_m3[0])/(sqrt(n_m3[0]*n_m3[0] + 3*n_m3[1]*n_m3[1] + 4*n_m3[2]*n_m3[2] - 2*sqrt(3)*n_m3[0]*n_m3[1])));

			A_mid = -(C_p[0] - sqrt(3)*C_p[1] + 2*r)/C_p[2];
			B_mid = (C_p[0]*C_p[0] + C_p[1]*C_p[1] + C_p[2]*C_p[2] + L2*L2 - L1*L1 - r*r)/(2*C_p[2]);
			C_mid = A_mid*A_mid + 4;
			D_mid = 2*A_mid*B_mid + 4*r;
			E_mid = B_mid*B_mid - L2*L2 + r*r;

			C_r[0] = (-D_mid - sqrt(D_mid*D_mid - 4*C_mid*E_mid))/(2*C_mid);
			C_r[1] = -sqrt(3)*C_r[0];
			C_r[2] = sqrt(L2*L2 - 4*r*C_r[0] - 4*C_r[0]*C_r[0] - r*r);

			angle = atan(C_r[2]/(sqrt(C_r[0]*C_r[0] + C_r[1]*C_r[1]) - r))*rad_to_deg;
			if (isnan(angle)){
				angle = 90;
			}

			angle = angle/2;
			break;

		default: // in case of an error
			angle = 0;
			break;
	}
	return angle;
}

void CF_IMU1(float x_a1, float y_a1, float z_a1, float x_g1, float y_g1, float z_g1){
	A[0] = atan((y_a1*gravity)/(z_a1*gravity));
	A[1] = atan((-x_a1*gravity)/sqrt(pow((y_a1*gravity), 2) + pow((z_a1*gravity), 2)));
	A[2] = 0; // g

	G[0] = prev_IMU1[0] + ((x_g1*(deg_to_rad))/416); // /416
	G[1] = prev_IMU1[1] + ((y_g1*(deg_to_rad))/416);
	G[2] = prev_IMU1[2] + ((z_g1*(deg_to_rad))/416);

	theta_xIMU1 = alpha*G[0] + (1-alpha)*A[0];
	phi_yIMU1 = alpha*G[1] + (1-alpha)*A[1];
	psi_zIMU1 = alpha*G[2] + (1-alpha)*A[2];

	prev_IMU1[0] = theta_xIMU1;
	prev_IMU1[1] = phi_yIMU1;
	prev_IMU1[2] = psi_zIMU1;
}

void CF_IMU2(float x_a2, float y_a2, float z_a2, float x_g2, float y_g2, float z_g2){
	A[0] = atan((y_a2*gravity)/(z_a2*gravity));
	A[1] = atan((-x_a2*gravity)/sqrt(pow((y_a2*gravity), 2) + pow((z_a2*gravity), 2)));
	A[2] = 0; // g

	G[0] = prev_IMU2[0] + ((x_g2*(deg_to_rad))/416);
	G[1] = prev_IMU2[1] + ((y_g2*(deg_to_rad))/416);
	G[2] = prev_IMU2[2] + ((z_g2*(deg_to_rad))/416);

	theta_xIMU2 = alpha*G[0] + (1-alpha)*A[0];
	phi_yIMU2 = alpha*G[1] + (1-alpha)*A[1];
	psi_zIMU2 = alpha*G[2] + (1-alpha)*A[2];

	prev_IMU2[0] = theta_xIMU2;
	prev_IMU2[1] = phi_yIMU2;
	prev_IMU2[2] = psi_zIMU2;
}

void OrientationEst1(){
	LSM6DSOX_readIMU1(vals); // get values from LSM6DSOX gyro and accel <- cup
	x_accIMU1 = vals[0];
	y_accIMU1 = vals[1];
	z_accIMU1 = vals[2]; // g

	x_gyroIMU1 = vals[3];
	y_gyroIMU1 = vals[4];
	z_gyroIMU1 = vals[5]; // dps

	CF_IMU1(x_accIMU1, y_accIMU1, z_accIMU1, x_gyroIMU1, y_gyroIMU1, z_gyroIMU1);
	cup_pitch_xSP = theta_xIMU1*rad_to_deg;
	cup_roll_ySP = phi_yIMU1*rad_to_deg;
}

void OrientationEst2(){
	LSM6DSOX_readIMU2(vals); // get values from LSM6DSOX gyro and accel <- car
	x_accIMU2 = vals[0];
	y_accIMU2 = vals[1];
	z_accIMU2 = vals[2]; // g

	x_gyroIMU2 = vals[3];
	y_gyroIMU2 = vals[4];
	z_gyroIMU2 = vals[5]; // dps

	CF_IMU2(x_accIMU2, y_accIMU2, z_accIMU2, x_gyroIMU2, y_gyroIMU2, z_gyroIMU2); // get orientation from comp filter
	car_pitch_xSP = theta_xIMU2*rad_to_deg;
	car_roll_ySP = phi_yIMU2*rad_to_deg;
}

// ----------------------------------------------------------------------------------------------
// Timer Callbacks
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim){
	if (htim->Instance == TIM16) { // only PWM timer for motor delays
		PWM_counter++; // 10 ms -> (1/96 MHz)*9600*100
		OrientationEst1();
		OrientationEst2();

		// Update data for transmission
		txData[0] = car_pitch_xSP;
		txData[1] = car_roll_ySP;
		txData[2] = cup_pitch_xSP;
		txData[3] = cup_roll_ySP;
		txData[4] = x_force; //PID_p_tx; //
		txData[5] = y_force; //PID_r_tx; //;
	}
}

void CalcTime(){  // integral and derivative timer for PID
	curr_timer_val = __HAL_TIM_GET_COUNTER(&htim17); // 100 microseconds counter

	if (curr_timer_val > prev_timer_val){ // in microseconds
		timer_diff = curr_timer_val - prev_timer_val;
	}
	else if (curr_timer_val < prev_timer_val){ // buffer overflow
		timer_diff = (65535 - prev_timer_val) + curr_timer_val;
	}
	prev_timer_val = curr_timer_val;
}

void HAL_UART_TxCpltCallBack(UART_HandleTypeDef *huart){
	if (huart -> Instance == USART2){
		HAL_UART_Transmit_IT(&huart2, (const uint8_t*)txData, 6*sizeof(txData)); // enable transmit again
	}
}

//// ----------------------------------------------------------------------------------------------
//// Other code functions for debugging
//
//void FF(){
//	// Averaging function
//	x_acc_average[0] = x_force*gravity;
//	x_filtered = (x_acc_average[0] + x_acc_average[1] + x_acc_average[2] + x_acc_average[3] + x_acc_average[4] + x_acc_average[5] + x_acc_average[6] + x_acc_average[7])/(8);
//	for (int i = 7; i > 0; i --){
//		x_acc_average[i] = x_acc_average[i - 1];
//	}
//
//	y_acc_average[0] = y_force*gravity;
//	y_filtered = (y_acc_average[0] + y_acc_average[1] + y_acc_average[2] + y_acc_average[3] + y_acc_average[4] + y_acc_average[5] + y_acc_average[6] + y_acc_average[7])/(8);
//	for (int i = 7; i > 0; i --){
//		y_acc_average[i] = y_acc_average[i - 1];
//	}
//
//	if (flag_v1 == 0){
//		z_acc_average[0] = (0)*gravity;
//		flag_v1 = 1;
//	}
//	else{
//		z_acc_average[0] = (z_force - 1)*gravity;
//	}
//	z_filtered = (z_acc_average[0] + z_acc_average[1] + z_acc_average[2] + z_acc_average[3] + z_acc_average[4] + z_acc_average[5] + z_acc_average[6] + z_acc_average[7])/(8);
//	for (int i = 7; i > 0; i --){
//		z_acc_average[i] = z_acc_average[i - 1];
//	}
//
//	pitch_tilt_ang = atan(x_filtered/(g + z_filtered))*rad_to_deg;
//	roll_tilt_ang = atan(y_filtered/(g + z_filtered))*rad_to_deg;
//}

//void PPController(){
//	MotorTime();
//	for (int i = 0; i < 2; i++){
//		if (i == 0){
//			velocity[i] = (car_pitch_xSP_copy - prev_xSP)/motor_curr_timer;
//
//			if (isnan(velocity[i])){
//				velocity[i] = 0;
//			}
//
//			velocity[i] = (alpha_PP[i]*velocity[i]) + (1.0 - alpha_PP[i])*velocity_prev[i];
//			PP[i] = -K[0]*car_pitch_xSP_copy - K[1]*velocity[i] + Kdc*(car_pitch_xSP_copy);
//		}
//		else {
//			velocity[i] = (car_roll_ySP_copy - prev_ySP)/motor_curr_timer;
//
//			if (isnan(velocity[i])){
//				velocity[i] = 0;
//			}
//
//			velocity[i] = (alpha_PP[i]*velocity[i]) + (1.0 - alpha_PP[i])*velocity_prev[i];
//			PP[i] = -K[0]*car_pitch_xSP_copy - K[1]*velocity[i] + Kdc*(car_pitch_xSP_copy);
//
//		}
//
//		velocity_prev[i] = velocity[i];
//		prev_xSP = car_pitch_xSP_copy;
//		prev_ySP = car_roll_ySP_copy;
//	}
//
//	if (PP[0] < 0){
//		PP[0] = -PP[0]; // make positive
//		pitch_flag = 1; // negative error
//	}
//
//	if (PP[1] < 0){
//		PP[1] = -PP[1]; // make positive
//		roll_flag = 1;
//	}
//
//	ActuateMotors(PP[0], PP[1]); // angle setpoint
//	cup_pitch_xSP_copy = cup_pitch_xSP;
//	cup_roll_ySP_copy = cup_roll_ySP;
//	PWM_counter = 0;
//
//}
//
//
// Transmits theta_x, phi_y, psi_z of comp filter to computer for verification
//void Transmit_CF_PC(){
////	theta_xIMU1 = theta_xIMU1*rad_to_deg;
////	phi_yIMU1 = phi_yIMU1*rad_to_deg;
////	psi_zIMU1 = psi_zIMU1*rad_to_deg;
////
////	theta_xIMU2 = theta_xIMU2*rad_to_deg;
////	phi_yIMU2 = phi_yIMU2*rad_to_deg;
////	psi_zIMU2 = psi_zIMU2*rad_to_deg;
////
////	printf("%E", phi_yIMU1); // Phi // roll
////	printf(",");
////	printf("%E", theta_xIMU1); // Theta // pitch
////	printf(",");
////	printf("%E", psi_zIMU1); // Psi
////	printf(",");
////	printf("%E", phi_yIMU2); // Phi // roll
////	printf(",");
////	printf("%E", theta_xIMU2); // Theta // pitch
////	printf(",");
////	printf("%E\n", psi_zIMU2); // Psi
//
////	printf("%E", cup_roll_ySP); // Phi // roll
////	printf(",");
////	printf("%E", cup_pitch_xSP); // Theta // pitch
////	printf(",");
//	printf("%E", car_roll_ySP); // Phi // roll
//	printf(",");
//	printf("%E\n", car_pitch_xSP); // Theta // pitch
//}
//
//
//// Performs Magdwick cals for filter
//void Magdwick(){
//	A[0] = x_accIMU1;
//	A[1] = y_accIMU1;
//	A[2] = z_accIMU1; // g
//
//	G[0] = 0;
//	G[1] = x_gyroIMU1*deg_to_rad;
//	G[2] = y_gyroIMU1*deg_to_rad;
//	G[3] = z_accIMU1*deg_to_rad; // rad/s
//
//	// F-matrix
//	F[0] = 2*(Q[1]*Q[3] - Q[0]*Q[2]) - A[0];
//	F[1] = 2*(Q[0]*Q[1] + Q[2]*Q[3]) - A[1];
//	F[2] = 2*(0.5 - pow(Q[1], 2) - pow(Q[2], 2)) - A[2];
//
//	// J-matrix
//	J_1[0] = -2*Q[2];
//	J_1[1] = 2*Q[1];
//	J_1[2] = 0;
//
//	J_2[0] = 2*Q[3];
//	J_2[1] = 2*Q[0];
//	J_2[2] = -4*Q[1];
//
//	J_3[0] = -2*Q[0];
//	J_3[1] = 2*Q[3];
//	J_3[2] = -4*Q[2];
//
//	J_4[0] = 2*Q[1];
//	J_4[1] = 2*Q[2];
//	J_4[2] = 0;
//
//	// step = J'*F
//	step[0] = J_1[0]*F[0] + J_1[1]*F[1] + J_1[2]*F[2];
//	step[1] = J_2[0]*F[0] + J_2[1]*F[1] + J_2[2]*F[2];
//	step[2] = J_3[0]*F[0] + J_3[1]*F[1] + J_3[2]*F[2];
//	step[3] = J_4[0]*F[0] + J_4[1]*F[1] + J_4[2]*F[2];
//
//	// normalise step size
//	step[0] = step[0]/(sqrt(pow(step[0], 2) + pow(step[1], 2) + pow(step[2], 2) + pow(step[3], 2)));
//	step[1] = step[1]/(sqrt(pow(step[0], 2) + pow(step[1], 2) + pow(step[2], 2) + pow(step[3], 2)));
//	step[2] = step[2]/(sqrt(pow(step[0], 2) + pow(step[1], 2) + pow(step[2], 2) + pow(step[3], 2)));
//	step[3] = step[3]/(sqrt(pow(step[0], 2) + pow(step[1], 2) + pow(step[2], 2) + pow(step[3], 2)));
//
//	// Fusion algorithm
//	// qDot = 0.5*quatmultiply([q0 q1 q2 q3],[0 gyro(1) gyro(2) gyro(3)]) - B*step';
//	qDot[0] = 0.5*(G[0]*Q[0] - G[1]*Q[1] - G[2]*Q[2] - G[3]*Q[3]) - beta*step[0];
//	qDot[1] = 0.5*(G[0]*Q[1] + G[1]*Q[0] - G[2]*Q[3] + G[3]*Q[2]) - beta*step[1];
//	qDot[2] = 0.5*(G[0]*Q[2] + G[1]*Q[3] + G[2]*Q[0] - G[3]*Q[1]) - beta*step[2];
//	qDot[3] = 0.5*(G[0]*Q[3] - G[1]*Q[2] + G[2]*Q[1] + G[3]*Q[0]) - beta*step[3];
//
//	// New quaternion estimate
//	Q[0] = Q[0] + (qDot[0]/416); // Fs = 416 Hz
//	Q[1] = Q[1] + (qDot[1]/416);
//	Q[2] = Q[2] + (qDot[2]/416);
//	Q[3] = Q[3] + (qDot[3]/416);
//
//	// Normalise result
//	Q[0] = Q[0]/(sqrt(pow(Q[0], 2) + pow(Q[1], 2) + pow(Q[2], 2) + pow(Q[3], 2)));
//	Q[1] = Q[1]/(sqrt(pow(Q[0], 2) + pow(Q[1], 2) + pow(Q[2], 2) + pow(Q[3], 2)));
//	Q[2] = Q[2]/(sqrt(pow(Q[0], 2) + pow(Q[1], 2) + pow(Q[2], 2) + pow(Q[3], 2)));
//	Q[3] = Q[3]/(sqrt(pow(Q[0], 2) + pow(Q[1], 2) + pow(Q[2], 2) + pow(Q[3], 2)));
//
//}
//
//// Transmits theta_x, phi_y, psi_z of Magdwick to computer for verification
//void Transmit_Mag_PC(){
////	char identifierA = 'A';
////	sprintf((char*)send, "%c, %.2f, %.2f,%.2f\n", identifierA, theta_x, phi_y, psi_z);
//	//UART_RETURN_STATUS = HAL_UART_Transmit(&huart1, send, strlen(send), HAL_MAX_DELAY);
//	// Printing to console on uart3
//	theta_xIMU1 = (asin(-2*(Q[1])*Q[2] - Q[0]*Q[2]))*rad_to_deg;
//	phi_yIMU1 = (atan(2*(Q[0]*Q[1] + Q[2]*Q[3])/(pow(Q[0], 2) - pow(Q[1], 2) - pow(Q[2], 2) + pow(Q[3], 2))))*rad_to_deg;
//	psi_zIMU1 = (atan(2*(Q[0]*Q[3] + Q[1]*Q[2])/(pow(Q[0], 2) + pow(Q[1], 2) - pow(Q[2], 2) - pow(Q[3], 2))))*rad_to_deg;
//
//	printf("%E\n", phi_yIMU1); // Theta
//	printf("%E\n", theta_xIMU1); // Phi
//	printf("%E\n", psi_zIMU1); // Psi
//}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
