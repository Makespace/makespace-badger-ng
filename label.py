#!/usr/bin/env python3

from dataclasses import dataclass

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class Label:
    @dataclass(frozen=True)
    class Padding:
        left: int = 0
        top: int = 0
        right: int = 0
        bottom: int = 0

    class LabelLine:
        def __init__(self, font, line, boxes):
            self.font = font
            self.line = line
            self.boxes = boxes

            min_y = min([b[1] for b in boxes])
            max_y = max([b[3] for b in boxes])
            self.height = max_y - min_y

    # This is used as a kind of "template" guide for how to size the lines
    # A single line of text gets 90% of the label height,
    # Two lines of text get split so that the first line gets a maximum of 70% and the second 20%
    # The font size may still get scaled down from this percentage if it takes up
    # too much width
    __line_portions = [
        [ 0.9 ],             # Single line, 90% height
        [ 0.7, 0.2 ],        # Two lines
        [ 0.5, 0.2, 0.2 ], # Three lines
    ]

    def __mm_to_px(self, mm):
        return int((mm / 25.4) * self.dpi)

    def __init__(self, lines, dpi=300, size_mm=(89, 36), padding_mm=Padding(0, 0, 0, 0)):
        self.dpi = dpi
        self.res = [self.__mm_to_px(s) for s in size_mm]
        self.img = None
        self.padding = Label.Padding(
            left=self.__mm_to_px(padding_mm.left),
            top=self.__mm_to_px(padding_mm.top),
            right=self.__mm_to_px(padding_mm.right),
            bottom=self.__mm_to_px(padding_mm.bottom),
        )
        self.usable_res = [
            self.res[0] - (self.padding.left + self.padding.right),
            self.res[1] - (self.padding.top + self.padding.bottom),
        ]

        lines_copy = []
        # Make sure all entries are a list of entries
        for i, line in enumerate(lines):
            if not isinstance(line, list):
                lines_copy.append([line])
            else:
                lines_copy.append(line)
        self.lines = lines_copy

        # Assign the appropriate maximum line percentages
        if len(self.lines) <= len(Label.__line_portions):
            portions = Label.__line_portions[len(self.lines)-1]
            self.max_line_heights = [int(portions[i] * self.usable_res[1]) for i in range(len(self.lines))]
        else:
            max_height = int(0.9 / len(self.lines) * self.usable_res[1])
            self.max_line_heights = [int(max_height)]  * len(self.lines)

        size = self.max_line_heights[0]
        try:
            self.base_font = ImageFont.truetype(font="Arial.ttf", size=size)
        except OSError:
            print("Trying backup font for label creation")
            self.base_font = ImageFont.truetype(font="DejaVuSans.ttf", size=size)

    # Work out the appropriate font size for the line, based on the allowable
    # max_line_height, and the width of the image
    def __choose_line_size(self, idx):
        size = self.max_line_heights[idx]
        line = self.lines[idx]

        max_elem_width = self.usable_res[0] // len(line)

        # Binary search to find the maximum allowable size that fits
        max_font_size = size
        min_font_size = 1
        while True:
            # FIXME: There used to be a font cache, but it grew too large
            # and then font loading would fail. I thought "font_variant" would
            # fix that, but it doesn't.
            font = self.base_font.font_variant(size=size)

            total_gap_width = 0
            if len(line) > 1:
                # left, top, right, bottom
                gap_bbox = font.getbbox('  ')
                total_gap_width = (gap_bbox[2] - gap_bbox[0]) * (len(line) - 1)

            max_elem_width = (self.usable_res[0] - total_gap_width) // len(line)

            ok = True
            boxes = []
            # Get the bounding box for each element, anchored in the centre
            # If any element is too big, bail out early
            for elem in line:
                bbox = font.getbbox(elem, anchor='mm')
                if (bbox[2] - bbox[0]) > max_elem_width:
                    ok = False
                    break
                boxes.append(bbox)

            if ok:
                min_font_size = size
            else:
                max_font_size = size

            new_size = min_font_size + ((max_font_size - min_font_size) // 2)

            if new_size == size:
                return Label.LabelLine(font, line, boxes)
            else:
                del font

            size = new_size

            if size == 0:
                raise ValueError(f"couldn't fit {line}")

    def image(self):
        if self.img:
            return self.img

        # Monochrome, 1 byte-per-pixel, fill with white
        img = Image.new('1', self.res, 1)

        d = ImageDraw.Draw(img)

        # Work out the sizes for each line
        line_params = []
        for i, line in enumerate(self.lines):
            lp = self.__choose_line_size(i)

            line_params.append(lp)

        # Distribute the lines with an equal gap between them
        total_height = sum([lp.height for lp in line_params])
        spare_height = self.usable_res[1] - total_height
        line_gap = spare_height // len(self.lines)

        # Top and bottom gap is half the gap between lines
        line_top = (line_gap // 2) + self.padding.top
        for i, lp in enumerate(line_params):
            # Columns get distributed evenly among all elements
            # TODO: Is this really ideal? If the elements are very different
            # lengths, it looks strange
            col_width = self.usable_res[0] // len(lp.line)

            x = (col_width // 2) + self.padding.left
            for j, elem in enumerate(lp.line):
                d.text((x, line_top), elem, font=lp.font, fill=0, anchor='mt')
                x += col_width

            line_top += lp.height + line_gap

        self.img = img

        return img
