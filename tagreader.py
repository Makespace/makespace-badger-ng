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
        return tag.hex()
