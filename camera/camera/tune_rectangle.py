#!/usr/bin/env python3

print("importing modules")

import multiprocessing as mp
import datetime
import numpy as np
import argparse
import cv2
import signal

from functools import wraps
import errno
import os
import copy


def main():
	# load the image, clone it for output, and then convert it to grayscale
	print("loading image")
	image = cv2.imread("water_test.jpg")
	orig_image = np.copy(image)
	output = image.copy()
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	#cv2.imshow("Image", gray )
	#cv2.waitKey(0)

	#exit(666)

	for p1 in range(0,256,1):
		for p2 in range(0,256,1):
			print (p1,p2)
			filename="./rectangle/rect_%03d_%03d.jpg" % (p2,p1)
			#print(os.path.exists(filename))
			if not os.path.exists(filename):
				thresh = cv2.threshold(gray, p1, p2, cv2.THRESH_BINARY)[1]
				cv2.imwrite(filename,thresh)
			else:
				print("Skipping",filename)



	#cv2.imshow("Image", thresh)
	#cv2.waitKey(0)



	exit(666)

	html='<html><head><title>Water meter  test</title></head><body>'
	for index, pr in enumerate(poolresults):
		if pr is not None:
			pd = pooldata2[index][1:]
			#print(pd)
			#text="dp:%s minDist:%s p1:%s p2:%s radius:%s+-%s circles exp:%s" % (pd[0],pd[1],pd[2],pd[3],pd[4],pd[6],pd[5])
			bigfilename="./test/water_hc_result_%s_big.jpg" % index
			smallfilename="./test/water_hc_result_%s_small.jpg" % index
			html+='<a href="%s">' %  bigfilename
			html+='<img src="%s">' % smallfilename
			html+='</a>'
			#saveimage(text,orig_image,bigfilename, smallfilename, pr)

	html+='</body></html>'

	#print("Poolresults:",poolresults)
	#print("Number of matching results:",counter)

	f=open('rectangle_result.html',"w")
	f.write(html)
	f.close()

def saveimage(text,image,bigfilename,smallfilename,data):
	print("Saving image %s" % (bigfilename))
	output = np.copy(image)

	font = cv2.FONT_HERSHEY_SIMPLEX
	# org
	location = (50, 50)
	# fontScale
	fontScale = 1
	# color in BGR
	color = (0,255,255)
	# Line thickness of 2 px
	thickness = 2
	# Line type
	linetype = cv2.LINE_AA

	cv2.putText(output,text,location,font,fontScale,color,thickness,linetype)

	cv2.imwrite(bigfilename,output)

	scale_percent = 15 # percent of original size
	width = int(output.shape[1] * scale_percent / 100)
	height = int(output.shape[0] * scale_percent / 100)
	dim = (width, height)

	# resize image
	resized = cv2.resize(output, dim, interpolation = cv2.INTER_AREA)
	cv2.imwrite(smallfilename,resized)

def search4rectangles(instancedata):

	image,guess_dp,mindist,p1,p2,guess_radius, circles_expected,radius_tolerance, id = instancedata


	if id % 100 == 0:
		print(id)

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
			#print(" -> S4C id:", id," dp:", guess_dp," mind:", mindist," p1:",p1," p2:", p2, " guess_radius:", guess_radius, " radius_tolerance:",radius_tolerance)
			text="dp:%s minDist:%s p1:%s p2:%s radius:%s+-%s circles exp:%s" % (guess_dp, mindist,p1,p2,guess_radius,radius_tolerance, circles_expected)
			bigfilename="./test/water_hc_result_%s_big.jpg" % id
			smallfilename="./test/water_hc_result_%s_small.jpg" % id
			saveimage(text,image,bigfilename,smallfilename,circles)


	return(circles)


if __name__ == "__main__":
    main()
