#Nick Mast
#Nov 2017

###############################################################################
#webcamAutomater
#
# A script to automate webcam catures
###############################################################################

import sys
import subprocess
import time
import datetime
import os
import re
import argparse
from argparse import ArgumentParser, ArgumentTypeError

def capture_image():
	fileName="cam"+get_trailing_number(args.device)+"_00001.png"

	#This silently grabs the cam image using ffmpeg
	command="ffmpeg -f video4linux2 -i "+args.device+" -vframes 1 -y -loglevel panic "+fileName
	#print command 
	
	print subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
	#At this point the image should be saved as something like 'cam1_00001.png'

	return

def update_website_image():
	fileName="cam"+get_trailing_number(args.device)+"_00001.png"
	
	if not os.path.exists(fileName):
		print "Error in update_website_image: "+fileName+" does not exist."
		return
	
	#Send a copy to the K100 monitoring page folder
	command="cp "+fileName+" /home/webusers/cdms/public_html/cdms_restricted/K100/thermometers/tempMon/images/MB_image.png"
	print subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
	return

def make_timestamped_copy():
	#We want to rename this with the current date and time	
	fileName_old="cam"+get_trailing_number(args.device)+"_00001.png"
	
	if not os.path.exists(fileName_old):
		print "Error in make_timestamped_copy: "+fileName_old+" does not exist."
		return
	

	dt=str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
	fileName_new="images/cam1_image_"+dt+".png"
	
	os.rename(fileName_old, fileName_new)

	return

def get_trailing_number(s):
	m = re.search(r'\d+$', s)
	return str(int(m.group())) if m else ""

###############################################################################
# this is the standard boilerplate that allows this to be run from the command line
###############################################################################
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Get capture info')
	parser.add_argument('-single',action='store_true',default=False,help='take a single image')
	parser.add_argument('-delay_min',type=float,help='delay between captures in minutes')
	parser.add_argument('-total_time_hr',type=float,help='total time to run in hours')
	parser.add_argument('-save_images', action='store_true',default=False,help='whether to save every image or just the most recent')
	parser.add_argument('-update_website', action='store_true',default=False,help='Update the current cam image on the K100 monitoring website')
	parser.add_argument('-device', type=str,default='/dev/video0',help='Webcam to use. Default is /dev/video0')
	
	args = parser.parse_args()
	if not (args.delay_min is None): delay_sec=args.delay_min*60.0
	startTime=time.time()

	if not os.path.exists(args.device):
		print "webcamAutomater error: "+args.device+" does not exist."
		sys.exit(1)

	if(args.single):
		#Take a single image
		capture_image()

		if args.update_website: update_website_image()
		if args.save_images: make_timestamped_copy()

	elif (args.total_time_hr is None):
		#Loop until the user kills it

		try:
			while True:
				capture_image()
				if args.update_website: update_website_image()
				if args.save_images: make_timestamped_copy()
				#Wait out the remaining time for this interval
				time.sleep(delay_sec-(time.time()-startTime)%delay_sec)
		except KeyboardInterrupt:
			pass
	else:
		#Loop until time expires or the user kills it
		total_time_sec=args.total_time_hr*3600.
		try:
			while (time.time()-startTime<total_time_sec):
				capture_image()
				if args.update_website: update_website_image()
				if args.save_images: make_timestamped_copy()
				#Wait out the remaining time for this interval
				time.sleep(delay_sec-(time.time()-startTime)%delay_sec)
		except KeyboardInterrupt:
			pass


