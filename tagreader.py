#!/usr/bin/env python3

import serial

class TagReader():
    def __init__(self, port):
        self.ser = serial.Serial(port, rtscts=1, timeout=0.2)

    def read_tag(self):
        self.ser.write(b'U')
        self.ser.flush()
        response = self.ser.read()
        if len(response) == 0 or response[0] == 0xc0:
            return None

        tag = self.ser.read(4)
        if len(tag) != 4:
            return None
        return tag

    def read_buttons(self):
        # 0 -- neither button pressed
        # 1 -- Edit button pressed
        # 2 -- QR button pressed
        # 3 -- Both buttons pressed

        buttons = 0
        self.ser.setDTR(False)
        if self.ser.getDSR():
            buttons += 1

        self.ser.setDTR(True)
        if self.ser.getDSR():
            buttons += 2

        return buttons
