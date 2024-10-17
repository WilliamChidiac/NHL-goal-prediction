from PIL import Image
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from ift6758.data import get_data
from typing import Tuple, List

heatmap_image_path = "../figures/heatmap_template.png"
heatmap = Image.open(heatmap_image_path)
half_length = 100
half_width = 85


def get_coord(x: int, y: int) -> Tuple[int, int]:
    length, width = heatmap.size
    image_coords_x = x / half_length * length
    image_coords_y = y / half_width * width
    if x < 0:
        x = -x
        y = -y
    return length - image_coords_x, image_coords_y


def plot_coords_on_heatmap(x_s: List[int], y_s: List[int], image=heatmap):
    x_pixel: List[float] = []
    y_pixel: List[float] = []
    for x, y in zip(x_s, y_s):
        image_coords_x, image_coords_y = get_coord(x, y)
        x_pixel.append(image_coords_x)
        y_pixel.append(image_coords_y)
    hm, xedges, yedges = np.histogram2d(x_pixel, y_pixel, bins=(100, 100))
    plt.imshow(
        heatmap, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], aspect="auto"
    )
    plt.imshow(
        hm.T,
        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
        origin="lower",
        cmap="hot",
        alpha=0.6,
    )
    plt.show()
