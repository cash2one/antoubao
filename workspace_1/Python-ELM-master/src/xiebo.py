import numpy as np
from scipy.ndimage import label, imread
from matplotlib.colors import ListedColormap
import pylab as pl

img = imread("figure_1.png")
img = img > 200

labeled, max_label = label(img)

pl.figure()
colors = [(0.0,0.0,0.0)] 
colors.extend(pl.cm.jet(np.linspace(0, 1, max_label))) 
cmap = ListedColormap(colors) 
im = pl.imshow(labeled, cmap=cmap)
cax = pl.colorbar()
pl.show()
