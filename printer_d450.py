#!/usr/bin/env python3

import usb.core
import usb.util

import multiprocessing

class PrinterDymo450():
    def __init__(self):
        dev = usb.core.find(idVendor=0x0922, idProduct=0x0020)
        if dev is None:
            raise ValueError('PrinterDymo450: device not found')
        self.dev = dev
        self.print_proc = None

        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

        dev.set_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]

        self.ep_out = usb.util.find_descriptor(intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)
        self.ep_in = usb.util.find_descriptor(intf,
            # match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)

        assert (self.ep_out is not None) and (self.ep_in is not None)

        self.reset()

    @property
    def dpi(self):
        return 300

    def padding(self):
        # XXX: There seems to be an unavoidable 5mm margin on the right edge,
        # So just scale down the label by 10mm.
        return (10, 0)

    def close(self):
        usb.util.dispose_resources(self.dev)
        self.dev = None

    def sync(self):
        self.write_command(0x1b, [0x1b] * 84)

    def reset(self):
        self.sync()
        self.write_command(ord('@'))

    def write_command(self, cmd, args=[]):
        buf = bytes([0x1b, cmd]) + bytes(args)
        self.ep_out.write(buf)

    def write_data(self, data=[]):
        buf = bytes([0x16]) + bytes(data)
        self.ep_out.write(buf)

    def get_status(self):
        self.write_command(ord('A'))

        status = self.ep_in.read(1)
        return status[0]

    def get_version(self):
        self.write_command(ord('V'))

        version = self.ep_in.read(10)
        return str(version.tobytes().decode())

    def form_feed(self):
        self.write_command(ord('E'))

    def short_form_feed(self):
        self.write_command(ord('G'))

    def __print_image(self, width, height, image_data):
        nbytes = (width + 7) // 8

        packed_lines = []

        for row in range(height):
            line = []
            for byte in range(nbytes):
                b = 0
                for bit in range(8):
                    col = (byte * 8) + bit
                    if col >= width:
                        break

                    idx = row * width + col
                    v = image_data[idx]
                    if v == 0:
                        # Scanline columns are MSB-first
                        # Determined empricially.
                        b |= (1 << (7 - bit))
                line.append(b)
            packed_lines.append(line)

        self.sync()
        self.write_command(ord('D'), [nbytes])

        nrows = len(packed_lines) + 100
        n1 = nrows // 256
        n2 = nrows % 256
        self.write_command(ord('L'), [n1, n2])

        for line in packed_lines:
            self.write_data(line)

        self.form_feed()

    def print_image(self, image, thread=False):
        # Always wait for any previous print job
        if self.print_proc:
            self.print_proc.join()
            self.print_proc = None

        width = image.width
        height = image.height
        image_data = image.getdata()

        if thread:
            self.print_proc = multiprocessing.Process(target=self.__print_image,
                                                      args=(width, height, image_data))
            self.print_proc.start()
        else:
            self.__print_image(width, height, image_data)

def main():
    printer = PrinterDymo450()

    printer.sync()

    # Bit 1 is top-of-form
    print("Initial, after sync:", printer.get_status())

    printer.form_feed()

    print("After form-feed:", printer.get_status())

    printer.write_command(ord('f'), [ord('1'), 200])

    print("After skip 200:", printer.get_status())

    printer.reset()

    print("After reset:", printer.get_status())

if __name__ == "__main__":
    main()
