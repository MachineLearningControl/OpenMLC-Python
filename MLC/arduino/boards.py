# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import usb.core
import usb.util

Due = {"NAME": "Arduino Due",
       "SHORT_NAME": "due",
       "ANALOG_PINS": range(54, 68),
       "DIGITAL_PINS": range(0, 54),
       "PWM_PINS": (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13),
       "ANALOG_DEFAULT_RESOLUTION": 12}

Uno = {"NAME": "Arduino Uno",
       "SHORT_NAME": "uno",
       "ANALOG_PINS": range(14, 20),
       "DIGITAL_PINS": range(0, 14),
       "PWM_PINS": (3, 5, 6, 9, 10, 11),
       "ANALOG_DEFAULT_RESOLUTION": 10}

Mega = {"NAME": "Arduino Mega",
        "SHORT_NAME": "mega",
        "ANALOG_PINS": range(54, 70),
        "DIGITAL_PINS": range(0, 54),
        "PWM_PINS": range(2, 14),
        "ANALOG_DEFAULT_RESOLUTION": 10}

Leonardo = {"NAME": "Arduino Leonardo",
            "SHORT_NAME": "leonardo",
            "ANALOG_PINS": range(14, 20),
            "DIGITAL_PINS": range(0, 14),
            "PWM_PINS": (3, 5, 6, 9, 10, 11, 12, 13),
            "ANALOG_DEFAULT_RESOLUTION": 10}

types = [Due, Uno, Mega, Leonardo]
boards_ids = [(0x2341, 0x0043, 1),
              (0x2341, 0x0042, 2),
              (0x2341, 0x8036, 3),
              (0x2341, 0x003e, 0),
              (0x03EB, 0x6124, 0)]

def detect_board():
    for id in boards_ids:
        usbdevs = usb.core.find(find_all=True, idVendor=id[0], idProduct=id[1])
        for dev in usbdevs:
            return id[2]
