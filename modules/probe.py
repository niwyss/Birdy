#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright 2015 Nicolas Wyss
#
# This file is part of BIRDY.
#
# BIRDY is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIRDY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BIRDY.  If not, see <http://www.gnu.org/licenses/>.

import argparse, sys, os, logging, cv2, time, cv2.cv as cv
from signal import *
import daemon
import imutils

class ProbeDaemon(daemon.Daemon):

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', logger = None):
        super(ProbeDaemon, self).__init__(pidfile, stdin, stdout, stderr)
        self.logger = logger
        self.detector = None

    def run(self):

        self.detector = MotionDetector(self.logger, 10)

        # Load the signal
        for sig in (SIGABRT, SIGINT, SIGTERM):
            signal(sig, self.signal_handler)

        self.detector.start()

    def signal_handler(self, signal, frame):
        self.detector.stop()

class MotionDetector():

    def __init__(self, logger = None, threshold = 25):

        # Log
        self.logger = logger

        # Time to work or not
        self.active = True

        #
        self.gray_frame = None
        self.average_frame = None
        self.absdiff_frame = None
        self.previous_frame = None

        self.surface = None
        self.currentsurface = 0
        self.currentcontours = None
        self.threshold = threshold

    def processImage(self, frame):

        # Remove false positives
        smooth_frame = frame
        cv.Smooth(frame, smooth_frame)

        # Compute the average
        cv.RunningAvg(smooth_frame, self.average_frame, 0.05)

        # Convert back to 8U frame
        cv.Convert(self.average_frame, self.previous_frame)

        # Moving_average - frame
        cv.AbsDiff(smooth_frame, self.previous_frame, self.absdiff_frame)

        # Convert to gray otherwise can't do threshold
        cv.CvtColor(self.absdiff_frame, self.gray_frame, cv.CV_RGB2GRAY)
        cv.Threshold(self.gray_frame, self.gray_frame, 50, 255, cv.CV_THRESH_BINARY)

        # To get object blobs
        cv.Dilate(self.gray_frame, self.gray_frame, None, 15)
        cv.Erode(self.gray_frame, self.gray_frame, None, 10)

    def somethingHasMoved(self):

        # Find contours
        storage = cv.CreateMemStorage(0)
        contours = cv.FindContours(self.gray_frame, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)

        # Save contours
        self.currentcontours = contours

        # For all contours compute the area
        while contours:
            self.currentsurface += cv.ContourArea(contours)
            contours = contours.h_next()

        # Calculate the average of contour area on the total size
        avg = (self.currentsurface * 100) / self.surface

        # Put back the current surface to 0
        self.currentsurface = 0

        if avg > self.threshold:
            return True
        return False

    def stop(self):
        self.active = False

    def start(self):

        self.active = True

        # Log
        self.logger.info("Probe - Start")

        # Load the camera
        capture = cv.CaptureFromCAM(0)

        # Initialize the first frame in the video stream
        frame = cv.QueryFrame(capture)
        self.surface = frame.width * frame.height
        self.gray_frame = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        self.average_frame = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_32F, 3)
        self.absdiff_frame = cv.CloneImage(frame)
        self.previous_frame = cv.CloneImage(frame)
        cv.Convert(frame, self.average_frame)

        # Loop over the frames of the video
        while self.active:

            self.processImage(frame)

            if self.somethingHasMoved():

                # Log
                self.logger.info("Probe - Something moves !!")

                # Draw contours
                cv.DrawContours(frame, self.currentcontours, (0, 0, 255), (0, 255, 0), 1, 2, cv.CV_FILLED)

                # Save file
                current_time = time.strftime("%m.%d.%y-%H.%M.%S", time.localtime())
                output_name = '/tmp/probe-%s.jpg' % current_time
                cv.SaveImage(output_name, frame)

            # Grab the next frame
            frame = cv.QueryFrame(capture)

        # Quit the camera
        if capture is not None:
            del(capture)

        self.logger.info("Probe - Stop")
