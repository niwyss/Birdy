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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import sys
from twython import Twython
from twython import TwythonError
import settings

def send(message, picture):

    # Build Twython API
    api = Twython(settings.CONSUMER_KEY,
                  settings.CONSUMER_SECRET,
                  settings.ACCESS_KEY,
                  settings.ACCESS_SECRET)

	#time_now = time.strftime("%H:%M:%S") # get current time
	#date_now =  time.strftime("%d/%m/%Y") # get current date
	#tweet_txt = "Photo captured by @twybot at " + time_now + " on " + date_now

    try:

        # Send text message with picture
        if picture is not None:
            media_status = api.upload_media(media=picture)
            api.update_status(media_ids=[media_status['media_id']], status=message)

        # Send text message
        else:
            api.update_status(status=message)

    except TwythonError, error:
        print error
