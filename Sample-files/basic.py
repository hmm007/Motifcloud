#!/usr/bin/env python2
"""
motif generating from sample file
"""

from os import path
import matplotlib.pyplot as plt
from wordcloud import VisMotif

d = path.dirname(__file__)

# Read the whole text.
tex = open(path.join(d, 'motif.txt')).read()


motifcloud = VisMotif().generate(tex)

#print (wordcloud)

# Open a plot of the generated image.
plt.imshow(motifcloud)
plt.axis("off")
plt.show()
