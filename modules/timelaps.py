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

# Time to work or not
active = True

class TimeLapsDaemon(daemon.Daemon):

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', logger = None, timeinterval = 10):
        super(TimeLapsDaemon, self).__init__(pidfile, stdin, stdout, stderr)
        self.logger = logger
        self.timeinterval = timeinterval

    def run(self):
        start(self.logger, self.timeinterval)


def __signal_handler(signal, frame):

    global active
    active = False


def start(logger, timeinterval):

    # Log
    logger.info("TimeLaps - Start")

    # Load the signal
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, __signal_handler)

    # Load the camera
    capture = cv.CaptureFromCAM(0)

    while active:

        # Take picture with camera
        img = cv.QueryFrame(capture)

        # Save file
        current_time = time.strftime("%m.%d.%y-%H.%M.%S", time.localtime())
        output_name = '/tmp/timelaps-%s.jpg' % current_time
        cv.SaveImage(output_name, img)

        # Log
        logger.info("TimeLaps - Take a picture")

        # Wait a while until next shot
        time.sleep(timeinterval)

    # Quit the camera
    if capture is not None:
        del(capture)

    logger.info("TimeLaps - Stop")
