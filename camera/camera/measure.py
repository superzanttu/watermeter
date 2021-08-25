#!/usr/bin/env python3

import cv2
import numpy as np

def test():
	print("test: imread")
	img = cv2.imread('water_test.jpg')
	height, width = img.shape[:2]

	print("test: covert to gray")
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #convert to gray

	print("test: tune gray image")
	gray = cv2.medianBlur(gray,5)

	print("test: imwrite gray")
	cv2.imwrite('water_test_gray.jpg',gray)

	counter=0
	for p1 in [30,40,50,60]:
		for p2 in [30,40,50,60]:
			for mindist in [20,50,100,150]:
				for minradius in [50,100,300,500]:
					for maxradius in [50,100,300,500]:
						counter = counter + 1
						file="water_hc_%s_%s_%s_%s_%s.jpg" % (p1,p2,mindist,minradius,maxradius)
						print("Gen (%s): %s" % (counter,file))
						#print("test: hough circles")
						circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, mindist, param1=p1,param2=p2, minRadius=minradius, maxRadius=maxradius)

						print(circles)

						if not circles is None:
							print("test: gray to color")
							nimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

							circles = np.uint16(np.around(circles))
							print("test: draw circles")

							for i in circles[0,:]:
    								# draw the outer circle
    								cv2.circle(nimg,(i[0],i[1]),i[2],(0,255,0),2)
					    			# draw the center of the circle
					    			cv2.circle(nimg,(i[0],i[1]),2,(0,0,255),3)

							print("test: imwrite color with circles")
							cv2.imwrite(file,nimg)



def main():
	test()

if __name__=='__main__':
    main()
