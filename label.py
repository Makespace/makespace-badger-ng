#!/usr/bin/env python3

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class Label():
    class LabelLine():
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

    def __init__(self, lines, dpi=300, size_mm=(89, 36)):
        self.dpi = dpi
        self.res = [self.__mm_to_px(s) for s in size_mm]
        self.fonts = {}

        # Make sure all entries are a list of entries
        for i, line in enumerate(lines):
            if not isinstance(line, list):
                lines[i] = [line]
        self.lines = lines

        # Assign the appropriate maximum line percentages
        if len(self.lines) <= len(Label.__line_portions):
            portions = Label.__line_portions[len(self.lines)-1]
            self.max_line_heights = [int(portions[i] * self.res[1]) for i in range(len(self.lines))]
        else:
            max_height = int(0.9 / len(self.lines) * self.res[1])
            self.max_line_heights = [int(max_height)]  * len(self.lines)

    # Work out the appropriate font size for the line, based on the allowable
    # max_line_height, and the width of the image
    def __choose_line_size(self, idx):
        size = self.max_line_heights[idx]
        line = self.lines[idx]

        max_elem_width = self.res[0] // len(line)

        while True:
            # Load font at max line height
            font = self.fonts.get(size)
            if font is None:
                #TODO: Could use font_variant to save re-loading
                font = ImageFont.truetype(font="Arial.ttf", size=size)
                self.fonts[size] = font

            # left, top, right, bottom
            gap_bbox = font.getbbox('  ')
            gap_width = gap_bbox[2] - gap_bbox[0]
            max_elem_width = (self.res[0] // len(line)) - gap_width

            boxes = []
            # Get the bounding box for each element, anchored in the centre
            for elem in line:
                bbox = font.getbbox(elem, anchor='mm')
                boxes.append(bbox)

            # If any element is too big, reduce the font size and try again
            ok = True
            for bbox in boxes:
                if (bbox[2] - bbox[0]) > max_elem_width:
                    ok = False
                    size -= 1
                    break

            if ok:
                return Label.LabelLine(font, line, boxes)

            if size == 0:
                raise ValueError(f"couldn't fit {line}")

    def image(self):
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
        spare_height = self.res[1] - total_height
        line_gap = spare_height // len(self.lines)

        # Top and bottom gap is half the gap between lines
        line_top = line_gap // 2
        for i, lp in enumerate(line_params):
            # Columns get distributed evenly among all elements
            # TODO: Is this really ideal? If the elements are very different
            # lengths, it looks strange
            col_width = self.res[0] // len(lp.line)

            x = col_width // 2
            for j, elem in enumerate(lp.line):
                d.text((x, line_top), elem, font=lp.font, fill=0, anchor='mt')
                x += col_width

            line_top += lp.height + line_gap

        return img
