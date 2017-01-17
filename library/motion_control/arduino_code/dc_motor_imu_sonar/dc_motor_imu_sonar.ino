
/* 
This program is used for control arms with MX servos
version: 2015-12-17
*/
#include <ModbusMaster.h>
// library for timer. May not work for some mega
#include <TimerOne.h>
#define SERVO_NUM 2 
#define SONAR_NUM 5

// data length with pc
// receive data: switch point, goal speed, end speed, goal acceleration
int receive_num = 8;
// send data: current position (32bit), current_speed, distance diff, angle_z
int send_num = 14;

// flags
boolean timer_flag = false; // flag for timer
boolean command_flag = false;

// timer counter
int counter_for_transmition = 0;

// motor variable
ModbusMaster left_motor(2,1);               //串口2，左轮ID=1
ModbusMaster right_motor(2,2);              //串口2，右轮ID=2

int goal_flag = 0;
int goal_speed[2] = {0, 0};
int goal_acceleration[2] = {0, 0};
long switch_point[2] = {0, 0};
int end_speed[2] = {0, 0};
long initial_position[2] = {0, 0};

int current_speed[2] = {0, 0};
long current_position[2] = {0, 0};

long distance_diff[2] = {0, 0};

// imu variable
int error_count = 0;//帧校验错误计数
int accelaration_data[6] = {0, 0, 0, 0, 0, 0};
int angular_velocity_data[6] = {0, 0, 0, 0, 0, 0};
int angle_data[6] = {0, 0, 0, 0, 0, 0};


// sonar variable
int trig[SONAR_NUM] = {8,9,10,11,12};
int echo[SONAR_NUM] = {2,3,21,20,19};
int sonar_initial_time[SONAR_NUM]={0,0,0,0,0};
float sonar_distance[SONAR_NUM] = {0,0,0,0,0};
int counter_for_sonar = 0;  // counter for sonar
boolean timer_flag_for_sonar = false; // timer flag for sonar


void setup()
{
  unsigned long baudrate = 115200;
  // initialize Modbus communication baud rate
  left_motor.begin(baudrate);
  right_motor.begin(baudrate);
  
  // initialize serial port
  Serial2.begin(115200,SERIAL_8E1);
  Serial.begin(115200,SERIAL_8N1);
  
  
  // initialize IMU
  Serial3.begin(115200);
  delayMicroseconds(50);
  unsigned char string[3]={0xff,0xaa,0x52}; //串口发送命令，目前只用到Z轴初始化命令
  for (int i=0;i<3;i++){
    Serial3.write(string[i]);
  }
  error_count=0; // not used yet
  
  // initialize sonar pins
  for (int i = 0; i < 5; i++){
      pinMode(trig[i], OUTPUT); 
      pinMode(echo[i], INPUT); 
      digitalWrite(trig[i], LOW); 
  }
  //开启0到4外部中断，任意沿触发
  attachInterrupt(0,interrupt0,CHANGE);
  attachInterrupt(1,interrupt1,CHANGE);
  attachInterrupt(2,interrupt2,CHANGE);
  attachInterrupt(3,interrupt3,CHANGE);
  attachInterrupt(4,interrupt4,CHANGE);

  // initialize timer
  Timer1.initialize(50); // set a timer 
  Timer1.attachInterrupt(timer_one_isr); // attach the service routine her
}

void loop()
{
  // This is the main loop of arduino.
  
  // the loop keeps check the data from IMU
  receive_data_from_IMU();
  
  // make control move if the timer flag is true
  if (timer_flag){
    timer_flag = false; // after one control move, wait for the timer
    get_signal(); // read serial port
    get_state();
    write_signal();
    write_acceleration(goal_acceleration);
    control_speed();
  }
}

void control_speed()
{
  int command_speed[2] = {0, 0};
  for (int i = 0; i < SERVO_NUM; i++){
    distance_diff[i] = abs(current_position[i] - initial_position[i]);
    if (distance_diff[i] >= switch_point[i]){
      command_speed[i] = end_speed[i];
    }
    else{
      command_speed[i] = goal_speed[i];
    }
  }
  write_speed(command_speed);
}

void write_acceleration(int acceleration[2])
{
  int result;
  //写左轮加速度
  left_motor.setTransmitBuffer(0, acceleration[0]);
  left_motor.setTransmitBuffer(1, acceleration[0]);
  result = left_motor.writeMultipleRegisters(0x52, 2);
  //写右轮加速度
  right_motor.setTransmitBuffer(0, acceleration[1]);
  right_motor.setTransmitBuffer(1, acceleration[1]);
  result = right_motor.writeMultipleRegisters(0x52, 2);
}

void write_speed(int speed_command[2])
{
  int result;
  //写左轮速度
   result = left_motor.writeSingleRegister(0x43, speed_command[0]);
  //写右轮速度
   result = right_motor.writeSingleRegister(0x43, speed_command[1]);
}

void get_state()
{
  int result;
  //读左轮状态，从0x22寄存器开始读，连续读4个寄存器
  result = left_motor.readHoldingRegisters(0x22, 4);
  
  if (result == left_motor.ku8MBSuccess)
  {
    current_speed[0] = left_motor.getResponseBuffer(0);
    current_position[0] = left_motor.getResponseBuffer(2);
    current_position[0] = (current_position[0]<<16) + left_motor.getResponseBuffer(3);
  }
  //读right轮状态，从0x22寄存器开始读，连续读4个寄存器
  result = right_motor.readHoldingRegisters(0x22, 4);
  if (result == right_motor.ku8MBSuccess)
  {
    current_speed[1] = right_motor.getResponseBuffer(0);
    current_position[1] = right_motor.getResponseBuffer(2);
    current_position[1] = (current_position[1]<<16)+right_motor.getResponseBuffer(3);
  }
  if (command_flag){
    command_flag = false;
    initial_position[0] = current_position[0];
    initial_position[1] = current_position[1];
  }
}

void receive_data_from_IMU()
{
  int sum;
  int imu_data[11];
  int temp_trash = 0;
  if(Serial3.available() >= 11){
    imu_data[0] = Serial3.read();
    if (imu_data[0] != 0x55) return;
    // read data
    for (int i = 0; i < 10; i++){
      imu_data[i+1] = Serial3.read();
    }
    // calculate checksum, sum = sum(imu_data[0:9])
    sum = 0;
    for (int j = 0; j < 10; j++){
      sum = sum + imu_data[j];
    }
    if (sum > 0xFF){
      sum = sum & 0x00FF;
    }
    // if checksum is correct save data
    if (sum == imu_data[10]){
      // the second digit indicate which data is transmitted
      switch(imu_data[1]){
        // acceleration
        case 0x51:
          for (int k = 0; k < 6; k++){
            accelaration_data[k] = imu_data[k+2];
          }
          break;
        
        // angular velocity
        case 0x52:
          for (int k = 0; k < 6; k++){
            angular_velocity_data[k] = imu_data[k+2];
          }
          break;
        
        // angle
        case 0x53:
          for (int k = 0; k < 6; k++){
            angle_data[k] = imu_data[k+2];
          }
          // temp_count ++ ;
          break;
      }
    }
    // if checksum is not correct, count error sum
    else{
      error_count++;
    }
  }
}

void get_signal()
{
  int temp_trash = 0;
  int temp;
  if(Serial.available() >= (3 + 2 * receive_num)){
    temp = Serial.read();
    goal_flag = Serial.read();
    for (int j = 0; j < SERVO_NUM; j++)
    {
      switch_point[j] = Serial.read();
      switch_point[j] = switch_point[j] + (Serial.read() << 8);
      goal_speed[j] = Serial.read();
      goal_speed[j] = goal_speed[j] + (Serial.read() << 8);
      end_speed[j] = Serial.read();
      end_speed[j] = end_speed[j] + (Serial.read() << 8);
      goal_acceleration[j] = Serial.read();
      goal_acceleration[j] = goal_acceleration[j] + (Serial.read() << 8);
    }
    temp = Serial.read();
    goal_speed[0] = -goal_speed[0];
    end_speed[0] = -end_speed[0];
    command_flag = true;
  }
}

void write_signal()
{
  int angle_z;
  Serial.write('n'); // inform the upper computer
  Serial.write(goal_flag); 
  for (int i = 0; i < SERVO_NUM; i++){
    if (i == 0){
      Serial.write(-current_position[i] & 0xff);
      Serial.write((-current_position[i] >> 8) & 0xff);
      Serial.write((-current_position[i] >> 16) & 0xff);
      Serial.write((-current_position[i] >> 24) & 0xff);
      Serial.write(-current_speed[i] & 0xff);
      Serial.write((-current_speed[i] >> 8) & 0xff);
    }
    else{
      Serial.write(current_position[i] & 0xff);
      Serial.write((current_position[i] >> 8) & 0xff);
      Serial.write((current_position[i] >> 16) & 0xff);
      Serial.write((current_position[i] >> 24) & 0xff);
      Serial.write(current_speed[i] & 0xff);
      Serial.write((current_speed[i] >> 8) & 0xff);
    }
    Serial.write(goal_speed[i] & 0xff);
    Serial.write((goal_speed[i] >> 8) & 0xff);
  }
  // send z-axis angle data
  angle_z = int(1800.0 / 32768.0 * (angle_data[5] << 8 | angle_data[4]));
  angle_z = angle_z + 1800;
  Serial.write(angle_z & 0xff);
  Serial.write((angle_z >> 8) & 0xff);
  
  // send sonar data
  for (int i = 0; i < SONAR_NUM; i++){
    Serial.write(int(sonar_distance[i]) & 0xff);
    Serial.write((int(sonar_distance[i]) >> 8) & 0xff);
  }
  
}

// This is the function at timer interrupt. It just change timer flag.
void timer_one_isr(){
  /////////////////////////////////////////////////////////
  // set timer 50ms get    timer_flag = true 
  if (timer_flag_for_sonar == true)
  {
    timer_flag_for_sonar = false;
    // send a ranging signal
    ultrasonic_ranging();
  }
  
  counter_for_sonar ++;
  // reset sonar counter. the cycle is 100ms
  if(counter_for_sonar >= 4000)
  {
    timer_flag_for_sonar = true;
    counter_for_sonar = 0;
  }
  
  
  counter_for_transmition ++;
  // reset transmition counter. The cycle is 20 ms
  if (counter_for_transmition >= 400){
    timer_flag = true;
    counter_for_transmition = 0;
  }
}

void ultrasonic_ranging()
{
  int trig_pin;
  counter_for_sonar = 0;
  for (int i = 0; i < SONAR_NUM; i++)
  {
    sonar_initial_time[i] = 0;
    sonar_distance[i] = 274;
    
    trig_pin = trig[i];
    digitalWrite(trig_pin, LOW); 
    delayMicroseconds(2); 
    digitalWrite(trig_pin, HIGH); 
    delayMicroseconds(10);
    digitalWrite(trig_pin, LOW); 
  }
}

//超声波外部中断
void interrupt0()
{ 
  if(digitalRead(echo[0]) == HIGH){
    sonar_initial_time[0] = counter_for_sonar;
    }
  else{
    sonar_distance[0] = (counter_for_sonar - sonar_initial_time[0]) * 1.735 / 2;
    }
}

void interrupt1()
{ 
  if(digitalRead(echo[1]) == HIGH){
    sonar_initial_time[1] = counter_for_sonar;
    }
  else{
    sonar_distance[1] = (counter_for_sonar - sonar_initial_time[1]) * 1.735 / 2;
    }
}

void interrupt2()
{ 
  if(digitalRead(echo[2]) == HIGH){
    sonar_initial_time[2] = counter_for_sonar;
    }
  else{
    sonar_distance[2] = (counter_for_sonar - sonar_initial_time[2]) * 1.735 / 2;
    }
}

void interrupt3()
{ 
  if(digitalRead(echo[3]) == HIGH){
    sonar_initial_time[3] = counter_for_sonar;
    }
  else{
    sonar_distance[3] = (counter_for_sonar - sonar_initial_time[3]) * 1.735 / 2;
    }
}

void interrupt4()
{ 
  if(digitalRead(echo[4]) == HIGH){
    sonar_initial_time[4] = counter_for_sonar;
    }
  else{
    sonar_distance[4] = (counter_for_sonar - sonar_initial_time[4]) * 1.735 / 2;
    }
}


