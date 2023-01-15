#!/usr/bin/env python3

import usb.core
import usb.util

class PrinterDymo450():
    def __init__(self):
        dev = usb.core.find(idVendor=0x0922, idProduct=0x0020)
        if dev is None:
            raise ValueError('Device not found')
        self.dev = dev

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

        assert (ep_out is not None) and (ep_in is not None)

    def reset(self):
        self.write_command(0x1b, [0x1b] * 84)
        self.write_command(ord('*'))

    def write_command(self, cmd, args=[]):
        buf = bytes([0x1b, cmd]) + bytes(args)
        self.ep_out.write(buf)

    def get_status(self):
        self.write_command(ord('A'))

        status = self.ep_in.read(1)
        return status[0]

    def get_version(self):
        self.write_command(ord('V'))

        version = self.ep_in.read(10)
        return str(version)

    def form_feed(self):
        self.write_command(ord('E'))

    def short_form_feed(self):
        self.write_command(ord('G'))

    def print_image(self, image):
        nbytes = (image.width + 7) // 8

        packed_lines = []
        data = image.getdata()

        for row in range(image.height):
            line = []
            for byte in range(nbytes):
                b = 0
                for bit in range(8):
                    col = (byte * 8) + bit
                    if col >= image.width:
                        break

                    idx = row * image.width + col
                    v = data[idx]
                    if v == 0:
                        b |= (1 << bit)
                line.append(b)
            packed_lines.append(line)

        self.reset()
        self.write_command(ord('D'), [nbytes])

        nrows = image.height + 100
        n1 = nrows // 256
        n2 = nrows % 256
        self.write_command(ord('L'), [n1, n2])

        for line in packed_lines:
            self.write_command(0x16, line)

        self.form_feed()

def main():
    printer = PrinterDymo450()

    printer.reset()
    print(printer.get_version())
    print(printer.get_status())
    printer.form_feed()
    #img = Image.new('1', (425, 1051), 1)
    #printer.print_image(img)

if __name__ == "__main__":
    main()
