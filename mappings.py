# Hardcoded
GRID_TO_ACTIONS = {8:1, 7:1, 6:2, 5:3, 4:4, 3:5, 2:5, 1:6, 0:6}
GRID_TO_COORDINATES = {0:-1, 1:0.8, 2:0.6, 3:0.4, 4:0, 5:0.4, 6:0.6, 7:0.8, 8:1}

# if (x == 1 || x==0.8)
# {
#   servoGuide.write(80);
#   servoBase.write(58);
#   delay(90);
# }
# else if (x==0.4 || x==0.6)
# {
#   servoGuide.write(80);
#   servoBase.write(55);
#   delay(90);
# }
# else if (x == 0)
# {
#   servoGuide.write(90);  
#   delay(90);
#   servoBase.write(53);
# }
# else if (x==-0.4)
# {
#   servoGuide.write(80);
#   servoBase.write(49);
#   delay(90); 
# }
# else if (x==-0.6)
# {
#   servoGuide.write(80);
#   servoBase.write(49);
#   delay(90); 
# }
# else if (x==-0.8)
# {
#   servoGuide.write(80);
#   servoBase.write(47);
#   delay(90);
# }
# else if (x==-1)
# {