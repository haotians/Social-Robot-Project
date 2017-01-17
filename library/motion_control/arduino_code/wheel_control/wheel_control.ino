/*
This is the arduino code for controlling two stepper motors for wheels
version 2015-11-05
*/

// library for timer one.
#include <TimerOne.h>
// number of motors
#define SERVO_NUM 2 //number of servo

boolean timer_flag = false; // flag for timer

// define pins. the first digit is for the left wheel, the second is for the right wheel
int stepper_pwm_pin[SERVO_NUM] = {9, 10};   //stepper PWM
int stepper_dir_pin[SERVO_NUM] = {8, 11};   //stepper Direction , when stepper driver SW2 is OFF ,
int stepper_ena_pin[SERVO_NUM] = {7, 12};   //stepper ENA ,when ENA is HIGH ,disable the stepper
int stepper_alm_pin[SERVO_NUM] = {6, 13};   //stepper alarm,when is low ,alarm 

//command data send by seria
int goal_position[SERVO_NUM] = {0, 0};
int goal_speed[SERVO_NUM] = {0, 0};
int goal_direction[SERVO_NUM] = {0, 0};
int goal_flag = 0;
int current_position[SERVO_NUM] = {0, 0};
int current_speed[SERVO_NUM] = {40, 30};
int current_direction[SERVO_NUM] = {20, 10};
int current_flag = 10;

// counters to generate impulse 
int control_cycle_counter = 0;
int pwm_counter1[SERVO_NUM] = {0, 0};
int pwm_counter2[SERVO_NUM] = {0, 0};
int pwm_counter3[SERVO_NUM] = {0, 0};

// global variable for generate impulse
int number_total = 500;              // 500 = 1000 / 2
int stepper_number_impulse[SERVO_NUM] = {100, 100};
int stepper_number_divider[SERVO_NUM] = {100, 100};
int stepper_number_diff[SERVO_NUM] = {0, 0};
int stepper_number_gap[SERVO_NUM] = {0, 0};
boolean impulse_flag[SERVO_NUM] = {true, true};

void setup()
{
  // initialize serial port
  Serial.begin(9600);
  for (int i = 0; i < SERVO_NUM; i++){
    // initialize pings
    pinMode(stepper_pwm_pin[i],OUTPUT);
    pinMode(stepper_dir_pin[i],OUTPUT);
    pinMode(stepper_ena_pin[i],OUTPUT);
    pinMode(stepper_alm_pin[i],INPUT);
    // enable motors
    digitalWrite(stepper_ena_pin[i],LOW);
  }
  
  Timer1.initialize(50); // set a timer 
  Timer1.attachInterrupt( timer_one_isr ); // attach the service routine here
}

void loop()
{
  // make control move if the timer flag is true
  if ( timer_flag )
  {
    timer_flag = false; // after one control move, wait for the timer
    get_signal(); // read serial port
    
    interpolate_command();
    make_control();
  }
}

void interpolate_command(){
  // 1: stop the wheel if goal position has reached
  // 2: make sure speeds change slowly
  for (int i = 0; i < SERVO_NUM; i++){
    
    // part 1: if the wheel have reached goal position, stop the wheel
    if (current_position[i] >= goal_position[i]){
      goal_speed[i] = 0;
    }
    
    // part 2: make sure the speed diff between two ajacent control cycle is less than 5
    // if the goal direction is same as current_direction, change current speed
    if (goal_direction[i] == current_direction[i]){
      if (goal_speed[i] >= current_speed[i] + 5){
        current_speed[i] = current_speed[i] + 5;
      }
      else if (goal_speed[i] <= current_speed[i] - 5){
        current_speed[i] = current_speed[i] - 5;
      }
      else{
        current_speed[i] = goal_speed[i];
      }
    }
    // if the goal direction is different with current direction, first decrease speed to 0, then change direction
    else{
      if (current_speed[i] >= 5){
        current_speed[i] = current_speed[i] - 5;
      }
      else{
        current_speed[i] = 0;
        current_direction[i] = goal_direction[i];
      }
    }
  }
}

void make_control()
{
  // this function calculate the number of impulses needed for next cycle
  
  int temp = 0;
  for (int i = 0; i < SERVO_NUM; i++){
    // set motor direction
    if (current_direction[i] == 0){
      // disable motor
      digitalWrite(stepper_ena_pin[i],HIGH);
    }
    else{
      if (current_direction[i] == 1){
        // clockwise
        digitalWrite(stepper_ena_pin[i],LOW);
        digitalWrite(stepper_dir_pin[i],HIGH);
      }
      else if (current_direction[i] == 2){
        // counter-clockwise
        digitalWrite(stepper_ena_pin[i],LOW);
        digitalWrite(stepper_dir_pin[i],LOW);
      }
    }
    
    if (current_speed[i] == 0){
      // disable motor
      stepper_number_divider[i] = 2000; // set to a very large number 
      pwm_counter1[i] = 0;
      pwm_counter2[i] = 0;
      pwm_counter3[i] = 0;
    }
    // calculate the number of impulses
    else{
      // calculate the minimum gap length between two impulse
      stepper_number_divider[i] = number_total / current_speed[i];
      // calculate the number of impulses will generate if the gap between all impulses is the minimum gap length
      temp = number_total / stepper_number_divider[i];
      // calculate the number of extra impulses generated  
      stepper_number_diff[i] = temp - current_speed[i];
      if (stepper_number_diff[i] == 0){
        stepper_number_gap[i] = 500; //set to a very large number
      }
      else{
        // calculate the gap length to remove generated impulses
        stepper_number_gap[i] = temp / stepper_number_diff[i];
      }
      // modify the divider to fit in c code
      stepper_number_divider[i] = 2 * stepper_number_divider[i] - 1;
      // clear counters
      pwm_counter1[i] = 0;
      pwm_counter2[i] = 0;
      pwm_counter3[i] = 0;
    }
    
    if (current_direction[i] == goal_direction[i]){
      current_position[i] = current_position[i] + current_speed[i];
    }
    else{
      current_position[i] = current_position[i] - current_speed[i];
    }
  }
}

void get_signal()
{
  if(Serial.available() >= (1 + 4 * SERVO_NUM))
  {
    goal_flag = Serial.read();
    for (int j = 0; j < SERVO_NUM; j++)
    {
      // the data for each servo is two 16 bit data. So need to read the serial port four times
      goal_position[j] = Serial.read();
      goal_position[j] = goal_position[j] + (Serial.read() << 8);
      goal_speed[j] = Serial.read();
      goal_speed[j] = goal_speed[j] + (Serial.read() << 8);
      
      if (goal_speed[j] == 0){
        goal_direction[j] = 0;
      }
      else if (goal_speed[j] <= 250){
        goal_direction[j] = 1;
      }
      else{
        goal_direction[j] = 2;
        goal_speed[j] = ( goal_speed[j] - 250);
      }
      
      current_position[j] = 0;
    }
  }
  
  Serial.write('n'); // inform the upper computer
  
  int speed_temp = 0;
  Serial.write((current_flag & 0xff)); 
  for (int i = 0; i < SERVO_NUM; i++)
  {
    Serial.write((current_position[i] & 0xff));
    Serial.write(((current_position[i] >> 8) & 0xff));
    if (current_direction[i] == 2){
      speed_temp = current_speed[i] + 250;
    }
    Serial.write((speed_temp & 0xff));
    Serial.write(((speed_temp >> 8) & 0xff));
  }
}


// This is the function at timer interrupt. It just change timer flag.
void timer_one_isr()
{ 
 /////////////////////////////////////////////////////////
  // set timer 50ms get    timer_flag = true 
  control_cycle_counter ++ ;
  if(control_cycle_counter >= 1000)
  {
    timer_flag = true;
    control_cycle_counter = 0;
  }
///////////////////////////////////////////////////////////  

  for (int i = 0; i < SERVO_NUM; i++){
    if(impulse_flag[i])
    {
      // If the pin is at HIGH, just set to LOW.
      digitalWrite(stepper_pwm_pin[i], LOW);
      impulse_flag[i] = false;
    }
    else
    {
      // If the pin is at LOW, need to calculate whether to set it to HIGH
      
      // pwm_counter1 is used for record minimum gap
      pwm_counter1[i]++;
      if (pwm_counter1[i] == stepper_number_divider[i])
      {
        // If pwm_counter1 = divider, set to HIGH, except...
        pwm_counter1[i] = 0;
        // pwm_counter2 record whether to remove a impulse
        pwm_counter2[i]++;
        if (pwm_counter2[i] == stepper_number_gap[i])
        {
          // if pwm_counter2 = gap, remove it, except...
          pwm_counter2[i] = 0;
          pwm_counter1[i] = -1;
          // pwm_counter3 record the number of impulses have been removed
          pwm_counter3[i]++;
          if (pwm_counter3[i] > stepper_number_diff[i])
          {
            // if pwm_counter3 > diff, stop removing. Generate a impulse
            digitalWrite( stepper_pwm_pin[i], HIGH);
            impulse_flag[i] = true;
            pwm_counter1[i] = 0;
          }
        }
        else
        {
          // generate a impulse
          digitalWrite( stepper_pwm_pin[i], HIGH);
          impulse_flag[i] = true;
        }
      }
    }
  }
}

