# Messenger-basketball-reinforcement-learning
Using reinforcement learning to play basketball messenger with a robotic arm.

This project is inspired by [Joshua Riddell's implementation](https://github.com/JoshuaRiddell/messenger-basketball-player).

* [Results video](https://www.youtube.com/watch?v=baSNCdxkE-A)

## Requirments

### Software
* `Python 2.7`
* `OpenCV`
* `numpy`
* `Pillow`
* `pytesseract`
* `picamera`

### Hardware
(This is what we used for the project)
* Arduino UNO
* Raspberry Pi 2
* 3 servos TowerPro SG90
* 5V-2A DC Power supply
* Raspberry Pi camera
* Smartphone


## Modules

The project is based on 3 modules:
1. The computer vision (folder ```cv```) module that processes the video stream and extracts information from it. This information will be the input of the learning module.
2. The learning module (folder ```learning```), that takes the data extracted from the cv module as input and outputs the chosen action.
3. The inverse kinematics module (folder ```ik```), that takes an action as input and, via the inverse kinematics of the arm, computes the servo signals required to perform that action.

The way in which the modules relate to each other is illustrated below:

![relations](https://github.com/juangallostra/messenger-basketball-reinforcement-learning/blob/develop/resources/module_diagram.png)

### CV module

![cv](https://github.com/juangallostra/messenger-basketball-reinforcement-learning/blob/develop/resources/cv_grid.gif)

### IK module

This module contains the **Arduino** code that allows to:
1. Read via serial port a set of ```x, y, z``` coordinates.
2. Compute the inverse kinematics of the robot and obtain the joint angles that result in the end effector reaching the desired position.
3. Move the servos according to the obtained angles.

However, for the project we fixed both the `y` and `z` coordinates (since the only change between different ball positions is its `x` value). We also hardcoded inside the `ik.ino` file the set of actions we allowed the robot to perform as a set of target joint angles. The raspberry Pi is the responsible for sending through the serial both the position in coordinates of the ball and the action to be performed.

### Learning module

The most simple form of [Q-Learning](https://en.wikipedia.org/wiki/Q-learning) was used as Lebry's learning algorithm.

## Results

[Video](https://www.youtube.com/watch?v=baSNCdxkE-A)

