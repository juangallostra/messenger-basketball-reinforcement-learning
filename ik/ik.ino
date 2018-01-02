#include <Servo.h>

// Servo's definition
Servo servoGuide;
Servo servoBase;
Servo servoArm;

// Auxiliar variables
int receivedData = 0;
char incomingByte;
bool newData = false;
bool receivedX = false;
bool receivedY = false;
bool receivedZ = false;
bool receivedCoordinates = false;

// x,y,z coordinates of the desired position
float x, y, z;
// alpha, beta and gamm joint angles
int guideAngle, baseAngle, armAngle;
// robot parameters
// TODO: measure parameters
float z_1 = 1;
float l_1 = 1;
float l_2 = 1;
float l_3 = 1;


void setup() 
{
   Serial.begin(9600);
   servoGuide.attach(9);
   servoBase.attach(10);
   servoArm.attach(11);
}

void loop() 
{
    recvWithEndMarker();
    // Check if there is new data and process it accordingly
    if (newData)
    {
      processData();
    }
    if (receivedCoordinates)
    {
      computeJointAngles();
      moveJoints();
    }
}

// Helper functions
void recvWithEndMarker() 
{
   if (Serial.available() > 0)      // something came across serial 
   {    
    receivedData = 0;               // throw away previous receivedData
    while(1)                        // force into a loop until 'n' is received
    {                      
      incomingByte = Serial.read();
      if (incomingByte == '\n') 
        break;                      // exit the while(1), we're done receiving
      if (incomingByte == -1) 
        continue;                   // if no characters are in the buffer read() returns -1
      receivedData *= 10;           // shift left 1 decimal place
      // convert ASCII to integer, add, and shift left 1 decimal place
      receivedData = ((incomingByte - 48) + receivedData);
    }
    newData = true;
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
        receivedX = true;
      }
      else if (receivedData % 5 == 0)
      {
        y = receivedData/10;
        receivedY = true;
      }
      else
      {
        z = receivedData/10;
        receivedZ = true;
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
  armAngle = asin((z-z_1)/l_3);
  baseAngle = asin(x/sqrt(pow(l_3, 2)-pow(z-z_1, 2)));
  guideAngle = acos((y-l_2-sqrt(pow(l_3, 2)-pow(z-z_1, 2)-pow(x, 2)))/l_1);
  receivedCoordinates = false;
}

void moveJoints()
{
  // TODO: calibrate servos
  servoGuide.write(guideAngle);
  servoBase.write(baseAngle);
  servoArm.write(armAngle);
}

