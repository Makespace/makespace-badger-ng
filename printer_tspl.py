#!/usr/bin/env python3

import io
import usb.core
import usb.util

import multiprocessing

class PrinterTSPL():
    def __init__(self, vid, pid):
        dev = usb.core.find(idVendor=vid, idProduct=pid)
        if dev is None:
            raise ValueError('PrinterVretti420B: device not found')
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

    @property
    def dpi(self):
        return 203

    # In mm, (left, top, right, bottom)
    def padding(self):
        return (3, 0, 3, 0)

    def write_command(self, command_str):
        buf = bytes(f"\r\n{command_str}\r\n", "utf-8")
        self.ep_out.write(buf)

    def calibrate(self, label_mm, gap_mm):
        label_dots = int(label_mm * 8)
        gap_dots = int(gap_mm * 8)
        self.write_command(f"GAPDETECT {label_dots},{gap_dots}")

    def form_feed(self):
        self.write_command("FORMFEED")

    def home(self):
        self.write_command("HOME")

    def backfeed(self, distance_mm):
        dots = int(distance_mm * 8)
        self.write_command(f"BACKUP {dots}")

    def close(self):
        usb.util.dispose_resources(self.dev)
        self.dev = None

    def __print_image(self, width, height, image_data):
        nbytes = (width + 7) // 8

        buf = io.BytesIO()

        # TODO: I don't know why x offset of 70 is needed
        buf.write(bytes(f"\r\nBITMAP 70,0,{nbytes},{height},0,", "utf-8"))

        for row in range(height):
            line = bytearray(nbytes)
            for byte, _ in enumerate(line):
                b = 0xff
                for bit in range(8):
                    col = (byte * 8) + bit
                    if col >= width:
                        break

                    idx = row * width + col
                    v = image_data[idx]
                    if v == 0:
                        b &= ~(1 << (7 - bit))
                line[byte] = b
            buf.write(line)

        buf.write(b"\r\n")

        self.write_command(f"SIZE {height},{width}")
        self.write_command("DIRECTION 0")
        self.write_command("CLS")

        self.ep_out.write(buf.getvalue())

        self.write_command("PRINT 1,1")

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

class PrinterVretti420B(PrinterTSPL):
    def __init__(self):
        super().__init__(0x2d84, 0x71a9)

def main():
    printer = PrinterVretti420B()

    printer.calibrate(89, 5)

if __name__ == "__main__":
    main()
