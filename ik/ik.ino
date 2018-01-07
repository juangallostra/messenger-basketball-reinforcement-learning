#include <Servo.h>

// Servo's definition
Servo servoGuide;
Servo servoBase;
Servo servoArm;

// Auxiliar variables
int receivedData = 0;
int action;
char incomingByte;
bool newData = false;
bool receivedX = false;
bool receivedY = false;
bool receivedZ = false;
bool receivedCoordinates = false;
bool receivedAction = false;
bool receivingAction = false;
bool negativeValue = false;

// x,y,z coordinates of the desired position
float x, y, z;
// alpha, beta and gamm joint angles
float guideAngle, baseAngle, armAngle;
// robot parameters
float z_1 = 7.6;
// Length of the bar that connects the servo and the clip in cm
float l_1 = 4.5;
// Lenght of the clip in cm
float l_2 = 9;
// Length of the arm  in cm
float l_3 = 7.5;


void setup() 
{
   Serial.begin(9600);
   servoGuide.attach(9);
   servoBase.attach(10);
   servoArm.attach(11);

   servoGuide.write(30);
   servoBase.write(0);
   servoArm.write(0);
}

void loop() 
{
    recvWithEndMarker();
    // Check if there is new data and process it accordingly
    if (newData)
    {
      processData();
    }
    if (receivedCoordinates && receivedAction)
    {
      computeJointAngles();
      moveJoints();
      performAction();
      servoBase.write(0); // 53 is the inverse kinematics 0
      servoGuide.write(30);
      
    }
}

// Helper functions
void recvWithEndMarker() 
{
   if (Serial.available() > 0)      // something came across serial 
   {    
    receivedData = 0;              // throw away previous receivedData
    while(1)                        // force into a loop until 'n' is received
    {                      
      incomingByte = Serial.read();
      if (incomingByte == '\n') 
        break;                      // exit the while(1), we're done receiving
      else if (incomingByte == 'A')
      {
        receivingAction = true;
        continue;
      }
      else if (incomingByte == '-')
      {
        negativeValue = true;
        continue;
      }
      else if (incomingByte == -1)
      {
        continue;                // if no characters are in the buffer read() returns -1
      }
      else
      {
        receivedData *= 10;           // shift left 1 decimal place
        // convert ASCII to integer, add, and shift left 1 decimal place
        receivedData = ((incomingByte - 48) + receivedData);
      }
    }
    newData = true;
    if (negativeValue)
    {
      receivedData = - receivedData;
      negativeValue = false;
    }
    else if (receivingAction)
    {
      newData = false;
      action = receivedData;
      receivedAction = true;
      Serial.print("A: ");
      Serial.println(receivedData);
      receivingAction = false;
    }
  }
}

void processData()
{
      // if number ends with 2 it is x coordinate, if it ends with
      // 5 it is y coordinate and else it is z coordinate
      // We divide by 10 to wipeout the marker number that indicates
      // the coordinate and store only the coordinate value.
      if (receivedData % 2 == 0)
      {
        x = receivedData/10;
        x = x/10.0;
        receivedX = true;
        Serial.println('X');
        Serial.println(x);
      }
      else if (receivedData % 5 == 0)
      {
        y = receivedData/10;
        y = y / 10.0;
        receivedY = true;
        Serial.println('Y');
        Serial.println(y);
      }
      else
      {
        z = receivedData/10;
        z = z / 10.0;
        receivedZ = true;
        Serial.println('Z');
        Serial.println(z);
      }
      
      if (receivedX && receivedY && receivedZ)
      {
        receivedCoordinates = true;
        receivedX = false;
        receivedY = false;
        receivedZ = false;
      }
      newData = false;
}

void computeJointAngles()
{
  // TODO: Conisder quadrants
  armAngle = asin((z-z_1)/l_3)*180.0/PI;
  baseAngle = asin(x/(l_3*cos(armAngle*PI/180.0)))*180.0/(PI+0.0);
  guideAngle = acos((y-l_2-(l_3*cos(armAngle*PI/180.0)*cos(baseAngle*PI/180.0)))/l_1)*180/PI;
  //guideAngle = acos((y-l_2-sqrt(pow(l_3, 2)-pow(z-z_1, 2)-pow(x, 2)))/l_1)*180/PI;
  receivedCoordinates = false;
  Serial.print("Arm: ");
  Serial.println(armAngle);
  Serial.print("Base: ");
  Serial.println(baseAngle);
  Serial.print("Guide: ");
  Serial.println(guideAngle);
  
}

void moveJoints()
{
  // TODO: calibrate servos
  // Taking into account our 0 is when the servo 0 is at 120 degrees
  servoGuide.write(170-guideAngle);
  //servoGuide.write(int(guideAngle));
  servoBase.write(int(53+baseAngle));
  delay(500);
  servoArm.write(int(-1*(armAngle+16)));
}

void performAction()
{
      delay(1000);
      if (action == 1)
      {
        servoGuide.write(80);
        servoBase.write(62);
        delay(90);
      }
      else if (action == 2)
      {
        servoGuide.write(80);
        servoBase.write(61);
        delay(90);
      }
      else if (action == 3)
      {
        servoGuide.write(80);
        servoBase.write(60);
        delay(90);
      }
      else if (action == 4)
      {
        servoGuide.write(80);
        servoBase.write(59);
        delay(90);
      }
      else if (action == 5)
      {
        servoGuide.write(80);
        servoBase.write(58);
        delay(90);
      }
      else if (action == 6)
      {
        servoGuide.write(80);
        servoBase.write(57);
        delay(90);
      }
      else if (action == 7)
      {
        servoGuide.write(80);
        servoBase.write(56);
        delay(90);
      }
      else if (action == 8)
      {
        servoGuide.write(80);
        servoBase.write(55);
        delay(90);
      }
      else if (action == 9)
      {
        servoGuide.write(80);
        servoBase.write(54);
        delay(90);
      }
      else if (action == 10)
      {
        servoGuide.write(90);  
        delay(90);
        servoBase.write(53);
      }
      else if (action == 11)
      {
        servoGuide.write(80);
        servoBase.write(52);
        delay(90);
      }
      else if (action == 12)
      {
        servoGuide.write(80);
        servoBase.write(51);
        delay(90);
      }
      else if (action == 13)
      {
        servoGuide.write(80);
        servoBase.write(50);
        delay(90);
      }
      else if (action == 14)
      {
        servoGuide.write(80);
        servoBase.write(49);
        delay(90);
      }
      else if (action == 15)
      {
        servoGuide.write(80);
        servoBase.write(48);
        delay(90);
      }
      else if (action == 16)
      {
        servoGuide.write(80);
        servoBase.write(47);
        delay(90);
      }
      else if (action == 17)
      {
        servoGuide.write(80);
        servoBase.write(46);
        delay(90);
      }
      else if (action == 18)
      {
        servoGuide.write(80);
        servoBase.write(45);
        delay(90);
      }
      
      //servoBase.write(53);
      servoArm.write(0);
      delay(1000);
      receivedAction = false;

}

