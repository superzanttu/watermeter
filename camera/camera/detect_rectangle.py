#!/usr/bin/env python3

print("importing modules")

import multiprocessing as mp
import datetime
import numpy as np
import argparse
import cv2
import signal
import imutils

from functools import wraps
import errno
import os
import copy

class ShapeDetector:
	def __init__(self):
		pass
	def detect(self, c):
		# initialize the shape name and approximate the contour
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)
		# if the shape is a triangle, it will have 3 vertices
		if len(approx) == 3:
			shape = "triangle"
		# if the shape has 4 vertices, it is either a square or
		# a rectangle
		elif len(approx) == 4:
			# compute the bounding box of the contour and use the
			# bounding box to compute the aspect ratio
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)
			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
		# if the shape is a pentagon, it will have 5 vertices
		elif len(approx) == 5:
			shape = "pentagon"
		# otherwise, we assume the shape is a circle
		else:
			shape = "circle"
		# return the name of the shape
		return shape

def main():
	# load the image, clone it for output, and then convert it to grayscale
	print("loading image")
	image_original = cv2.imread("water_test.jpg")
	#ratio = image.shape[0] / float(resized.shape[0])
	ratio=1.0
	output = image_original.copy()
	gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
	cv2.imshow("Gray", gray)
	cv2.waitKey(0)

	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	cv2.imshow("Blurred", blurred)
	cv2.waitKey(0)

	thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
	cv2.imshow("Tresh", thresh)
	cv2.waitKey(0)

	#cv2.imshow("Image", gray )
	#cv2.waitKey(0)

	# find contours in the thresholded image and initialize the
	# shape detector
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	sd = ShapeDetector()

	# OpenCV shape detection
	# loop over the contours
	for c in cnts:
		# compute the center of the contour, then detect the name of the
		# shape using only the contour
		M = cv2.moments(c)
		cX = int((M["m10"] / M["m00"]) * ratio)
		cY = int((M["m01"] / M["m00"]) * ratio)
		shape = sd.detect(c)
		# multiply the contour (x, y)-coordinates by the resize ratio,
		# then draw the contours and the name of the shape on the image
		c = c.astype("float")
		c *= ratio
		c = c.astype("int")
		cv2.drawContours(output, [c], -1, (0, 255, 0), 2)
		cv2.putText(output, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (255, 255, 255), 2)
		# show the output image
		cv2.imshow("Image", output)
		cv2.waitKey(0)

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
