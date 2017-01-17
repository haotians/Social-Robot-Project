/* 
This program is used for control arms with MX servos
version: 2015-11-10
 */

// library for timer. May not work for some mega
#include <MsTimer2.h>  

#define SERVO_NUM 10 //number of servo

boolean timer_flag = false; // flag for timer
boolean initial_flag = false;

//command data send by seria
int goal_position_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int goal_position_high[SERVO_NUM] = {8, 8, 8, 8, 8, 8, 8, 8, 8, 8};
int goal_speed_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int goal_speed_high[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int goal_flag = 0;

int current_position_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 20, 0, 0, 0};
int current_position_high[SERVO_NUM] = {0, 10, 0, 0, 0, 0, 0, 0, 0, 0};
int current_speed_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int current_speed_high[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

boolean set_flag = false;
int torque_enable[SERVO_NUM] = {0, 0, 0, 0, 1, 1, 1, 1, 1, 1};   // initial disable
int led_enable[SERVO_NUM]={1,1,1,1,1,1,1,1,1,1};
int pid_kp[SERVO_NUM] = {32, 32, 32, 32, 32, 32, 32, 32, 32, 32};  
int pid_ki[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int pid_kd[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

int current_flag = 0;

int servo_request_count = 1;

// head pins
int neck_direction[2] = {6, 7};
int neck_pwm = 5;
int neck_position = 0;

int false_check = 0;

void setup()
{
  // initialize serial port
  Serial.begin(115200);
  Serial2.begin(200000,SERIAL_8N1); //Serial1 on pins 19 (RX) and 18 (TX)
  
  // initialize neck pins
  pinMode(neck_direction[0], OUTPUT);
  pinMode(neck_direction[1], OUTPUT);
  pinMode(neck_pwm, OUTPUT);
  
  // initialize timer
  MsTimer2::set(20, change_timer_flag);  
  MsTimer2::start();
}

void loop()
{
  // This is the main loop of arduino.
  // make control move if the timer flag is true
  if ( timer_flag ){
    timer_flag = false; // after one control move, wait for the timer
    get_signal(); // read serial port
    make_control();
  }
}

void make_control()
{
  if (set_flag == true){
    set_flag = false;
    move_arm();
    move_head();
  }
  update_arm_status();
}

void move_arm(){
  switch (goal_flag){
    case 1:
      // release the torque
      send_dynamixel_one_paramater(0x18);
      break;
    case 2:
      // set P parameter/q
      send_dynamixel_one_paramater(0x1C);
      break;
    case 3:
      // set I parameter
      send_dynamixel_one_paramater(0x1B);
      break;
    case 4:
      // set D parameter
      send_dynamixel_one_paramater(0x1A);
      break;
    case 5:
      // do nothing
      break;
    default:
      if (initial_flag){
        // move servo to goal position with goal speed
        send_dynamixel_position_speed();
      }
  }
}

void move_head(){
  
  if (neck_position == 0){
    digitalWrite(neck_direction[0],HIGH);
    digitalWrite(neck_direction[1],LOW);
  }
  else{
    digitalWrite(neck_direction[0],LOW);
    digitalWrite(neck_direction[1],HIGH);
  }
  digitalWrite(neck_pwm,HIGH);
}

void update_arm_status(){
  for (int i = 0; i < 10; i++){
  // ask for status
  request_servo_status(servo_request_count);
  // receive servo status
  receive_data_from_servo();
  
  servo_request_count++;
  if (servo_request_count >= 11){
    servo_request_count = 1;
    }
    
  if (timer_flag){
    // if some servo return no feedback, break
    break;
    }
  }
}

void get_signal()
{
  int begin_flag;
  int end_flag;
  int temp_arm_data[4 * SERVO_NUM];
  int temp_trash;
  if(Serial.available() >= (3 + 4 * SERVO_NUM + 2 * 1)){
    begin_flag = Serial.read();
    if (begin_flag == 0xff){
      goal_flag = Serial.read();
      current_flag = goal_flag;
      for (int j = 0; j < 4 * SERVO_NUM; j++){
        temp_arm_data[j] = Serial.read();
      }
      switch (goal_flag){
        case 1:
          // when goal_flag = 1. release the servo to record trajectory
          break;
        case 2:
          // set P parameter
          for (int k = 0; k < SERVO_NUM; k++){
            pid_kp[k] = temp_arm_data[4*k];
          }
          break;
        case 3:
          // set I parameter
          for (int k = 0; k < SERVO_NUM; k++){
            pid_ki[k] = temp_arm_data[4*k];
          }
          break;
        case 4:
          // set D parameter
          for (int k = 0; k < SERVO_NUM; k++){
            pid_kd[k] = temp_arm_data[4*k];
          }
          break;
        case 5:
          // just move head
          break;
        default:
          for (int k = 0; k < SERVO_NUM; k++){
            // the data for each servo is two 16 bit data. So need to read the serial port four times
            goal_position_low[k] = temp_arm_data[4*k];
            goal_position_high[k] = temp_arm_data[4*k+1];
            goal_speed_low[k] = temp_arm_data[4*k+2];
            goal_speed_high[k] = temp_arm_data[4*k+3];
          }
          initial_flag = true;
      }
      
      neck_position = Serial.read();
      neck_position = neck_position + (Serial.read() << 8);
      end_flag = Serial.read();
      if (end_flag == 0xee){
        set_flag = true;
      }
      else{
        false_check = Serial.available();
        while(Serial.available() > 0){
          temp_trash = Serial.read();
        }
        set_flag = false;
        false_check ++;
      } 
    }
    else{
      while(Serial.available() > 0){
        temp_trash = Serial.read();
      }
      // false_check ++;
    }
  }

  // send status to pc
  Serial.write('n'); // inform the upper computer
  
  Serial.write(false_check); 
  for (int i = 0; i < SERVO_NUM; i++){
    Serial.write(current_position_low[i]);
    Serial.write(current_position_high[i]);
    Serial.write(current_speed_low[i]);
    Serial.write(current_speed_high[i]);
  }
}

void send_dynamixel_position_speed()
{
  byte checksum = 0;
  unsigned int sum = 0;
  
  Serial2.write(0xFF);// head 1
  Serial2.write(0xFF);// head 2
  Serial2.write(0xFE);// Broadcasting ID 254
  Serial2.write(0x36);// datalength ((4+1)*10+4=54)
  Serial2.write(0x83);// instruction SYNC WRITE control several RX-64s simultaneously 
  Serial2.write(0x1E);// position low regisiter address 
  Serial2.write(0x04);// every dynamixel position(2) and speed (2)length
  
  for(int i = 0; i < SERVO_NUM; i++){
    Serial2.write((i+1));
    Serial2.write(goal_position_low[i]);
    Serial2.write(goal_position_high[i]);
    Serial2.write(goal_speed_low[i]);
    Serial2.write(goal_speed_high[i]);
    sum = sum + (i + 1) + goal_position_low[i] + goal_position_high[i] + goal_speed_low[i] + goal_speed_high[i];
  }
  
  sum = sum + 0x1D9 ;  // ID 0x24= 1+2+3+4+5++6+7+8  //   0xFE+0x36+0x83+0x1E+0x04=0x1D9
  
  if(sum > 0xFF){
    sum = sum & 0x00FF ;
  }
  checksum = 0xFF - sum;
  Serial2.write(checksum);  //checkSUM
}

//torque enable address= 0x18; led address= 0x19; kd arrdess = 0x1A; ki address= 0x1B ; kp address =0x1C
void send_dynamixel_one_paramater(int start_address)
{
  byte checksum = 0;
  unsigned int sum = 0;
  if((start_address>=0x18)&&(start_address<=0x1C))
  {
      Serial2.write(0xFF);// head 1
      Serial2.write(0xFF);// head 2
      Serial2.write(0xFE);// Broadcasting ID 254
      Serial2.write(2*SERVO_NUM+4);// datalength ((1+1)*SERVO_NUM+4=20)
      Serial2.write(0x83);// instruction SYNC WRITE control several RX-64s simultaneously 
      Serial2.write(start_address);// position low regisiter address 
      Serial2.write(0x01);// one paramater
      
      for(int i = 0; i < SERVO_NUM; i++)
      {
        Serial2.write(i+1);
        switch(start_address){
           case 0x18: 
            Serial2.write(torque_enable[i]); 
            sum = sum + (i + 1) + torque_enable[i];
            break;
           case 0x19: 
            Serial2.write(led_enable[i]); 
            sum = sum + (i + 1) + led_enable[i];
            break;
           case 0x1A: 
            Serial2.write(pid_kd[i]); 
             sum = sum + (i + 1) + pid_kd[i];
            break;
           case 0x1B: 
            Serial2.write(pid_ki[i]);
            sum = sum + (i + 1) + pid_ki[i];
            break;
           case 0x1C: 
            Serial2.write(pid_kp[i]);
            sum = sum + (i + 1) + pid_kp[i];
            break;
           default:
            break;
        }
      }
      
      sum = sum + 0x182 + start_address + 2*SERVO_NUM+4;    //   0xFE+0x83+0x01=0x182
      if(sum > 0xFF){
        sum = sum & 0x00FF ;
      }
      checksum = 0xFF - sum;
      Serial2.write(checksum);  //checkSUM
  }
}

void request_servo_status(byte servo_id)
{
   byte checksum = 0;
   unsigned int sum = 0;
   sum = servo_id + 0x04 + 0x02 + 0x24 + 0x08 ;
   if(sum > 0xFF){
      sum = sum & 0x00FF ;
   }
   checksum = 0xFF - sum;
   Serial2.write(0xFF); //head 1
   Serial2.write(0xFF); //head 2
   Serial2.write(servo_id); //ID
   Serial2.write(0x04); //datalength (4)
   Serial2.write(0x02); //instruction read data from MX 
   Serial2.write(0x24); //the data address you want read
   Serial2.write(0x08); // the number of data 
   Serial2.write(checksum); //checkSUM
}

void receive_data_from_servo()   
{
  byte buffer[14]={0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  byte servo_id = 0;
  int temp_count = 0;
  while ( (temp_count < 14) ){
    if(Serial2.available() >= 1){
      buffer[temp_count] = Serial2.read();
      temp_count++;
    }
    if (timer_flag){
      break;
    }
  }
  if((buffer[0]==0xFF)&&(buffer[1]==0xFF)&&(buffer[3]==0x0A)&&(buffer[4]==0x00)){ 
    servo_id = buffer[2];
    current_position_low[servo_id - 1] = buffer[5];
    current_position_high[servo_id - 1] = buffer[6];
    current_speed_low[servo_id - 1] = buffer[7];
    current_speed_high[servo_id - 1] = buffer[8];
  }
}
// This is the function at timer interrupt. It just change timer flag.
void change_timer_flag(){
  timer_flag = true; 
}
