#!/usr/bin/env python3

print("importing modules")

import multiprocessing as mp
#import datetime
import numpy as np
#import argparse
import cv2
#import signal

#from functools import wraps
#import errno
#import os
#import copy


def main():
	# load the image, clone it for output, and then convert it to grayscale
	print("loading image")
	image = cv2.imread("water_test.jpg")
	orig_image = np.copy(image)
	output = image.copy()
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	circles = None

	# quesingparameters
	minimum_radius = 200     #this is the range of possible circle in pixels you want to find
	maximum_radius = 250     #maximum possible circle size you're willing to find in pixels
	radius_step = 3        # default 5
	radius_tolerance = 8   # default +-3

	circles_expected = 4          #we expect to find just one circle
	minDist = 100 # minimum distance between circles

	pooldata1 = []
	pooldata2 = []

	p1_min=44
	p1_max=49
	p1_step=2

	p2_min=100
	p2_max=40
	p2_step=-2

	dp_min=1
	dp_max=4
	dp_step = 0.5

	print("circles expected:",circles_expected)
	print("minimum distance:",minDist)
	print("radius:",minimum_radius,"-",maximum_radius,"step:",radius_step,"tolerance:",radius_tolerance)
	print("p1:", p1_min,"-",p1_max,"step:",p1_step)
	print("p2:", p2_min,"-",p2_max,"step:",p2_step)
	print("dp:",dp_min,"-",dp_max,"step:",dp_step)

	for dp in range(int(dp_min*10),int(dp_max*10),int(dp_step*10)):
		for p2 in range  (p2_min,p2_max,p2_step): # quessing treshhold 100 (max 300?) quality vote
			for p1 in range (p1_min,p1_max,p1_step):
				for radius in range (minimum_radius, maximum_radius, radius_step):
					vdata = (gray,
						float(dp/10),
						minDist,
						p1,
						p2,
						radius,
						circles_expected,
						radius_tolerance
					)

					pooldata1.append(vdata)

	print("Number of combinations to process:",len(pooldata1))



	id = len(pooldata1)
	for p in pooldata1:
		pooldata2.append(p + (id,))
		id-=1

	print("Creating pool")
	pool = mp.Pool()

	print("Multiprosessing combinations")
	poolresults = pool.map(search4circles, pooldata2)
	print("DONE")

def saveimage(text1,text2,image,filename,data):
	print("Saving image %s" % (filename))
	output = np.copy(image)

	font = cv2.FONT_HERSHEY_SIMPLEX
	# org
	location1 = (50, 50)
	location2 = (50, 90)
	# fontScale
	fontScale = 1
	# color in BGR
	color = (0,255,255)
	# Line thickness of 2 px
	thickness = 2
	# Line type
	linetype = cv2.LINE_AA

	cv2.putText(output,text1,location1,font,fontScale,color,thickness,linetype)
	cv2.putText(output,text2,location2,font,fontScale,color,thickness,linetype)

	circle = np.round(data[0, :]).astype("int")

	for (x, y, r) in circle:
		# draw the circle in the output image, then draw a rectangle
		# corresponding to the center of the circle
		cv2.circle(output, (x, y), r, (0, 255, 255), 2)
		cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

	cv2.imwrite(filename,output)

def search4circles(instancedata):

	image,guess_dp,mindist,p1,p2,guess_radius, circles_expected,radius_tolerance, id = instancedata


	if id % 100 == 0:
		print("Processing task:",id)

	#print("    S4C id:", id," dp:", guess_dp," mind:", mindist," p1:",p1," p2:", p2, " guess_radius:", guess_radius, " radius_tolerance:",radius_tolerance)

	circles = cv2.HoughCircles(image,
		cv2.HOUGH_GRADIENT,
		dp=guess_dp,               #resolution of accumulator array.
		minDist=mindist,                #number of pixels center of circles should be from each other, hardcode
		param1=p1,
		param2=p2,
		minRadius=(guess_radius-radius_tolerance),    #HoughCircles will look for circles at minimum this size
		maxRadius=(guess_radius+radius_tolerance)     #HoughCircles will look for circles at maximum this size
	)


	if circles is not None:
		if len(circles[0]) != circles_expected:
			return(None)
		else:
			if circlesOK(circles) is True:
				text1="dp:%s minDist:%s p1:%s p2:%s radius:%s+-%s circles exp:%s" % (guess_dp, mindist,p1,p2,guess_radius,radius_tolerance, circles_expected)
				text2=""
				filename="./test/water_ct_%02d_%04d_%04d_%s.jpg" % (guess_dp*10,p2,p1,id)
				saveimage(text1,text2,image,filename,circles)
			else:
				return(None)

	return(circles)

def circlesOK(data):

	c = np.round(data[0, :]).astype("int")
	#print("c:",c)

	ccount=4
	for i in range(0,ccount-1):
		for j in range(i+1,ccount):
			x1 = c[i][0]
			y1 = c[i][1]
			x2 = c[j][0]
			y2 = c[j][1]
			r1 = c[i][2]
			r2 = c[j][2]


			d = (abs(x1-x2)**2 + abs(y1-y2)**2)**0.5
			#print("xyr1:",x1,y1,r1)
			#print("xyr2:",x2,y2,r2)

			#print("d:",d)

			if (d < r1 + r2):
				return(False)

	return(True)



if __name__ == "__main__":
    main()
