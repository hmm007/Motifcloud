# Author: HMM <hmmpython@gmail.com>
# Copyright 2015
# License: See License file
import os
import re
import sys
import numpy
from operator import itemgetter
from random import Random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from .query_integral_image import query_integral_image
class VisMotif(object):
