#!/usr/bin/env python3

print("importing modules")

import datetime
import numpy as np
import argparse
import cv2
import signal

from functools import wraps
import errno
import os
import copy



# load the image, clone it for output, and then convert it to grayscale
print("loading image")
image = cv2.imread("meters.jpg")
print("transforming image", end=" ")
orig_image = np.copy(image)
print("...copy1", end=" ")
output = image.copy()
print("...copy2", end=" ")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

print("...done")
circles = None

minimum_circle_size = 50      #this is the range of possible circle in pixels you want to find
maximum_circle_size = 500     #maximum possible circle size you're willing to find in pixels

guess_dp = 1.0

number_of_circles_expected = 4          #we expect to find just one circle
breakout = False

#hand tune this
max_guess_accumulator_array_threshold = 100     #minimum of 1, no maximum, (max 300?) the quantity of votes 
                                                #needed to qualify for a circle to be found.
circleLog = []

guess_accumulator_array_threshold = max_guess_accumulator_array_threshold

while guess_accumulator_array_threshold > 1 and breakout == False:
    print("X")
    #start out with smallest resolution possible, to find the most precise circle, then creep bigger if none found
    guess_dp = 1.0
    #print("resetting guess_dp:" + str(guess_dp))
    while guess_dp < 9 and breakout == False:
        print("*")
        guess_radius = maximum_circle_size
        #print("setting guess_radius: " + str(guess_radius))
        #print(circles is None)
        while True:
            print(".", end="")

            #HoughCircles algorithm isn't strong enough to stand on its own if you don't
            #know EXACTLY what radius the circle in the image is, (accurate to within 3 pixels) 
            #If you don't know radius, you need lots of guess and check and lots of post-processing 
            #verification.  Luckily HoughCircles is pretty quick so we can brute force.

            #print("guessing radius: " + str(guess_radius) + " and dp: " + str(guess_dp) + " vote threshold: " + str(guess_accumulator_array_threshold))

            circles = cv2.HoughCircles(gray, 
                cv2.HOUGH_GRADIENT, 
                dp=guess_dp,               #resolution of accumulator array.
                minDist=50,                #number of pixels center of circles should be from each other, hardcode
                param1=50,
                param2=guess_accumulator_array_threshold,
                minRadius=(guess_radius-3),    #HoughCircles will look for circles at minimum this size
                maxRadius=(guess_radius+3)     #HoughCircles will look for circles at maximum this size
                )

            if circles is not None:
                if len(circles[0]) == number_of_circles_expected:
                    print("guessing radius: " + str(guess_radius) + " and dp: " + str(guess_dp) + " vote threshold: " + str(guess_accumulator_array_threshold))
                    print("len of circles: " + str(len(circles)))
                    circleLog.append(copy.copy(circles))
                break
                circles = None
            guess_radius -= 5 
            if guess_radius < 40:
                break;

        guess_dp += 1.5

    guess_accumulator_array_threshold -= 2

#Return the circleLog with the highest accumulator threshold
print("---circleLog")
print(circleLog)


# ensure at least some circles were found
for cir in circleLog:
    print("---cir")
    print(cir)
    # convert the (x, y) coordinates and radius of the circles to integers
    output = np.copy(orig_image)

    if (len(cir) > 1):
        print("FAIL before")
        exit()

    print(cir[0, :])

    cir = np.round(cir[0, :]).astype("int")

    # loop over the (x, y) coordinates and radius of the circles
    if (len(cir) > 1):
        print("FAIL after")
        exit()

    for (x, y, r) in cir:
        # draw the circle in the output image, then draw a rectangle
        # corresponding to the center of the circle
        cv2.circle(output, (x, y), r, (0, 0, 255), 2)
        cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    cv2.imwrite("water_hc_result_%s.jpg" % (datetime.datetime.now()),output)
