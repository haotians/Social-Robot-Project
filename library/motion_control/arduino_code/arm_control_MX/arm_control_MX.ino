/* 
This program is used for control arms with MX servos
version: 2015-11-10
 */

// library for timer. May not work for some mega
#include <MsTimer2.h>  

#define SERVO_NUM 8 //number of servo

boolean timer_flag = false; // flag for timer
boolean signal_flag = true; // flag for serial port
boolean initial_flag = false;

//command data send by seria
int goal_position_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};
int goal_position_high[SERVO_NUM] = {8, 8, 8, 8, 8, 8, 8, 8};
int goal_speed_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};
int goal_speed_high[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};
int goal_flag = 0;

int current_position_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};
int current_position_high[SERVO_NUM] = {0, 10, 0, 0, 0, 0, 0, 0};
int current_speed_low[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};
int current_speed_high[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};

boolean set_flag = false;
int torque_enable[SERVO_NUM] = {0, 0, 0, 0, 1, 1, 1, 1};   // initial disable
int led_enable[SERVO_NUM]={1,1,1,1,1,1,1,1};
int pid_kp[SERVO_NUM] = {32, 32, 32, 32, 32, 32, 32, 32};  
int pid_ki[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};
int pid_kd[SERVO_NUM] = {0, 0, 0, 0, 0, 0, 0, 0};

int current_flag = 0;

int servo_request_count = 1;

void setup()
{
  // initialize serial port
  Serial.begin(115200);
  Serial1.begin(200000,SERIAL_8N1); //Serial1 on pins 19 (RX) and 18 (TX)
  
  // initialize timer
  MsTimer2::set(20, change_timer_flag);  
  MsTimer2::start();
}

void loop()
{
  // This is the main loop of arduino.
  
  // read the serial port when mark is false
  if(signal_flag){
    signal_flag = false; // change the serial flag
    get_signal(); // read serial port
  }

  // make control move if the timer flag is true
  if ( timer_flag ){
    timer_flag = false; // after one control move, wait for the timer
    signal_flag = true;  // the serial can only read the serial port once per control cycle
    make_control();
  }
}

void make_control()
{
  if (set_flag == true){
    set_flag = false;
    switch (goal_flag){
      case 1:
        // release the torque
        send_dynamixel_one_paramater(0x18);
        break;
      case 2:
        // set P parameter
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
      default:
        if (initial_flag){
          // send command to servos
          send_dynamixel_position_speed();
        }
    }
  }
  /*
  for (int i = 0; i < 8; i++){
  // ask for status
  request_servo_status(servo_request_count);
  // receive servo status
  receive_data_from_servo();
  // due to time limit, we just ask for one servo status per one control cycle
  servo_request_count++;
  if (servo_request_count >= 9){
    servo_request_count = 1;
    }
  if (timer_flag){
    break;
    }
  }
  */
}

void get_signal()
{
  int temp_trash = 0;
  if(Serial.available() >= (1 + 4 * SERVO_NUM)){
    goal_flag = Serial.read();
    current_flag = goal_flag;
    set_flag = true;
    switch (goal_flag){
      case 1:
        // when goal_flag = 1. release the servo to record trajectory
        for (int j = 0; j < SERVO_NUM; j++){
          // just clear the serial port
          temp_trash = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
        }
        break;
      case 2:
        // set P parameter
        for (int j = 0; j < SERVO_NUM; j++){
          pid_kp[j] = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
        }
        break;
      case 3:
        // set I parameter
        for (int j = 0; j < SERVO_NUM; j++){
          pid_ki[j] = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
        }
        break;
      case 4:
        // set D parameter
        for (int j = 0; j < SERVO_NUM; j++){
          pid_kd[j] = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
          temp_trash = Serial.read();
        }
        break;
      default:
        for (int j = 0; j < SERVO_NUM; j++){
          // the data for each servo is two 16 bit data. So need to read the serial port four times
          goal_position_low[j] = Serial.read();
          goal_position_high[j] = Serial.read();
          goal_speed_low[j] = Serial.read();
          goal_speed_high[j] = Serial.read();
        }
        initial_flag = true;
    }
  }
  
  Serial.write('n'); // inform the upper computer
  
  Serial.write(current_flag); 
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
  
  Serial1.write(0xFF);// head 1
  Serial1.write(0xFF);// head 2
  Serial1.write(0xFE);// Broadcasting ID 254
  Serial1.write(0x2C);// datalength ((4+1)*8+4=44)
  Serial1.write(0x83);// instruction SYNC WRITE control several RX-64s simultaneously 
  Serial1.write(0x1E);// position low regisiter address 
  Serial1.write(0x04);// every dynamixel position(2) and speed (2)length
  
  for(int i = 0; i < SERVO_NUM; i++){
    Serial1.write((i+1));
    Serial1.write(goal_position_low[i]);
    Serial1.write(goal_position_high[i]);
    Serial1.write(goal_speed_low[i]);
    Serial1.write(goal_speed_high[i]);
    sum = sum + (i + 1) + goal_position_low[i] + goal_position_high[i] + goal_speed_low[i] + goal_speed_high[i];
  }
  
  sum = sum + 0x1CF ;  // ID 0x24= 1+2+3+4+5++6+7+8  //   0xFE+0x2C+0x83+0x1E+0x04=0x1CF
  
  if(sum > 0xFF){
    sum = sum & 0x00FF ;
  }
  checksum = 0xFF - sum;
  Serial1.write(checksum);  //checkSUM
}

//torque enable address= 0x18; led address= 0x19; kd arrdess = 0x1A; ki address= 0x1B ; kp address =0x1C
void send_dynamixel_one_paramater(int start_address)
{
  byte checksum = 0;
  unsigned int sum = 0;
  if((start_address>=0x18)&&(start_address<=0x1C))
  {
      Serial1.write(0xFF);// head 1
      Serial1.write(0xFF);// head 2
      Serial1.write(0xFE);// Broadcasting ID 254
      Serial1.write(2*SERVO_NUM+4);// datalength ((1+1)*SERVO_NUM+4=20)
      Serial1.write(0x83);// instruction SYNC WRITE control several RX-64s simultaneously 
      Serial1.write(start_address);// position low regisiter address 
      Serial1.write(0x01);// one paramater
      
      for(int i = 0; i < SERVO_NUM; i++)
      {
        Serial1.write(i+1);
        switch(start_address){
           case 0x18: 
            Serial1.write(torque_enable[i]); 
            sum = sum + (i + 1) + torque_enable[i];
            break;
           case 0x19: 
            Serial1.write(led_enable[i]); 
            sum = sum + (i + 1) + led_enable[i];
            break;
           case 0x1A: 
            Serial1.write(pid_kd[i]); 
             sum = sum + (i + 1) + pid_kd[i];
            break;
           case 0x1B: 
            Serial1.write(pid_ki[i]);
            sum = sum + (i + 1) + pid_ki[i];
            break;
           case 0x1C: 
            Serial1.write(pid_kp[i]);
            sum = sum + (i + 1) + pid_kp[i];
            break;
           default:
            break;
        }
      }
      
      sum = sum + 0x182 + start_address +2*SERVO_NUM+4;    //   0xFE+0x83+0x01=0x182
      if(sum > 0xFF){
        sum = sum & 0x00FF ;
      }
      checksum = 0xFF - sum;
      Serial1.write(checksum);  //checkSUM
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
   Serial1.write(0xFF); //head 1
   Serial1.write(0xFF); //head 2
   Serial1.write(servo_id); //ID
   Serial1.write(0x04); //datalength (4)
   Serial1.write(0x02); //instruction read data from MX 
   Serial1.write(0x24); //the data address you want read
   Serial1.write(0x08); // the number of data 
   Serial1.write(checksum); //checkSUM
}

void receive_data_from_servo()   
{
  byte buffer[14]={0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  byte servo_id = 0;
  int temp_count = 0;
  while ( (temp_count < 14) ){
    if(Serial1.available() >= 1){
      buffer[temp_count] = Serial1.read();
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
