# Author: HMM <hmmpython@gmail.com>
# Copyright 2015
# License: MIT See License file

# some code are taken from https://github.com/amueller/word_cloud
# detail descriptions are availabe there.
# those code are (c) 2012 Andreas Christian Mueller 
 

from random import Random
import os
import re
import sys
import numpy as numpy
from operator import itemgetter

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from .query_integral_image import query_integral_image

item1 = itemgetter(1)

#set the font
fontLoc = os.environ.get("FONT_PATH", "/Users/mac/Desktop/font mac/I.ttf")


def random_color_func(motif, font_size, position, orientation, random_state=None):
    if random_state is None:
        random_state = Random()
    return "hsl(%d, 100%%, 50%%)" % random_state.randint(0, 360)


class VisMotif(object):
    def __init__(self, font_path=None, width=1400, height=1200, margin=5,
                 ranks_only=False, prefer_horizontal=0.9, mask=None, scale=1,
                 color_func=random_color_func, max_motifs=20, random_state=None, background_color='yellow', max_font_size=None):
        
        font_path = fontLoc
        self.font_path = font_path
        self.width = width
        self.height = height
        self.margin = margin
        self.ranks_only = ranks_only
        self.prefer_horizontal = prefer_horizontal
        self.mask = mask
        self.scale = scale
        self.color_func = color_func
        self.max_motifs = max_motifs
        if isinstance(random_state, int):
            random_state = Random(random_state)
        self.random_state = random_state
        self.background_color = background_color
        if max_font_size is None:
            max_font_size = height
        self.max_font_size = max_font_size

    def fit_motifs(self, motifs):
        if self.random_state is not None:
            random_state = self.random_state
        else:
            random_state = Random()

        if len(motifs) <= 0:
            print("Your file conatains no motif, got %d."
                  % len(motifs))

        if self.mask is not None:
            width = self.mask.shape[1]
            height = self.mask.shape[0]
            integral = numpy.cumsum(numpy.cumsum(self.mask, axis=1), axis=0).astype(numpy.uint32)
        else:
            height, width = self.height, self.width
            integral = numpy.zeros((height, width), dtype=numpy.uint32)

        # create image
        img_grey = Image.new("L", (width, height))
        draw = ImageDraw.Draw(img_grey)
        img_array = numpy.asarray(img_grey)
        font_sizes, positions, orientations, colors = [], [], [], []

        font_size = self.max_font_size

        # start drawing grey image
        for motif, count in motifs:
            # alternative way to set the font size
            if not self.ranks_only:
                font_size = min(font_size, int(100 * numpy.log(count + 100)))
            while True:
                # try to find a position
                font = ImageFont.truetype(self.font_path, font_size)
                # transpose font optionally
                if random_state.random() < self.prefer_horizontal:
                    orientation = None
                else:
                    orientation = Image.ROTATE_90
                transposed_font = ImageFont.TransposedFont(font,
                                                           orientation=orientation)
                draw.setfont(transposed_font)
                # get size of resulting text
                box_size = draw.textsize(motif)
                # find possible places using integral image:
                result = query_integral_image(integral, box_size[1] + self.margin,
                                              box_size[0] + self.margin, random_state)
                if result is not None or font_size == 0:
                    break
                # if we didn't find a place, make font smaller
                font_size -= 1

            if font_size == 0:
                # we were unable to draw any more
                break

            x, y = numpy.array(result) + self.margin // 2
            # actually draw the text
            draw.text((y, x), motif, fill="white")
            positions.append((x, y))
            orientations.append(orientation)
            font_sizes.append(font_size)
            colors.append(self.color_func(motif, font_size, (x, y), orientation,
                                          random_state=random_state))
            # recompute integral image
            if self.mask is None:
                img_array = numpy.asarray(img_grey)
            else:
                img_array = numpy.asarray(img_grey) + self.mask
            # recompute bottom right
            # the order of the cumsum's is important for speed ?!
            partial_integral = numpy.cumsum(numpy.cumsum(img_array[x:, y:], axis=1),
                                         axis=0)
            # paste recomputed part into old image
            # if x or y is zero it is a bit annoying
            if x > 0:
                if y > 0:
                    partial_integral += (integral[x - 1, y:]
                                         - integral[x - 1, y - 1])
                else:
                    partial_integral += integral[x - 1, y:]
            if y > 0:
                partial_integral += integral[x:, y - 1][:, numpy.newaxis]

            integral[x:, y:] = partial_integral

        self.layout_ = list(zip(motifs, font_sizes, positions, orientations, colors))
        return self.layout_

    def process_text(self, text):

        d = {}
        flags = re.UNICODE if sys.version < '3' and \
                                type(text) is unicode else 0
        for motif in re.findall(r"\w[\w']*", text, flags=flags):
            if motif.isdigit():
                continue

            motif_lower = motif.lower()
            

            # Look in lowercase dict.
            if motif_lower in d:
                d2 = d[motif_lower]
            else:
                d2 = {}
                d[motif_lower] = d2

            # Look in any case dict.
            d2[motif] = d2.get(motif, 0) + 1

        d3 = {}
        for d2 in d.values():
            # Get the most popular case.
            first = max(d2.items(), key=item1)[0]
            d3[first] = sum(d2.values())

        for key in list(d3.keys()):
            if key.endswith('s'):
                key_singular = key[:-1]
                if key_singular in d3:
                    val_plural = d3[key]
                    val_singular = d3[key_singular]
                    d3[key_singular] = val_singular + val_plural
                    del d3[key]

        motifs = sorted(d3.items(), key=item1, reverse=True)
        motifs = motifs[:self.max_motifs]
        maximum = float(max(d3.values()))
        for i, (motif, count) in enumerate(motifs):
            motifs[i] = motif, count / maximum

        self.motifs_ = motifs

        return motifs
    def generate(self, text):
        self.process_text(text)
        self.fit_motifs(self.motifs_)
        return self


    def _check_generated(self):
        if not hasattr(self, "layout_"):
            raise ValueError("VisMotif has not been calculated, call generate first.")

    def to_image(self):
        self._check_generated()
        if self.mask is not None:
            width = self.mask.shape[1]
            height = self.mask.shape[0]
        else:
            height, width = self.height, self.width

        img = Image.new("RGB", (width * self.scale, height * self.scale), self.background_color)
        draw = ImageDraw.Draw(img)
        for (motif, count), font_size, position, orientation, color in self.layout_:
            font = ImageFont.truetype(self.font_path, font_size * self.scale)
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            pos = (position[1] * self.scale, position[0] * self.scale)
            draw.text(pos, motif, fill=color)
        return img
    def to_file(self, filename):
        img = self.to_image()
        img.save(filename)
        return self

    def to_array(self):
        return numpy.array(self.to_image())

    def __array__(self):
        return self.to_array()


