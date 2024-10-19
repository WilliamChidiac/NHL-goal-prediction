from PIL import Image
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from ift6758.data import get_data
from typing import Tuple, List
import plotly.graph_objects as go

heatmap_image_path = "../figures/heatmap_template.png"
heatmap = Image.open(heatmap_image_path)
half_length = 100
half_width = 85


def invert_period_coords(row):
    if row["periodDescriptor_number"] % 2 == 0:
        row["xCoord"] = -row["xCoord"]
        row["yCoord"] = -row["yCoord"]
    return row


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


rink_image_path = "../figures/nhl_rink.png"
rink_image = Image.open(rink_image_path)


def plot_coords_on_image_plotly(
    rink_coords: List[Tuple[int, int]], image=rink_image, debug_origin=False
) -> None:

    # Get dimensions
    image_length, image_height = image.size
    rink_length = 200
    rink_height = 85

    def feet_to_pixels(rink_coord_x, rink_coord_y):
        image_coords_x = rink_coord_x / rink_length * image_length
        image_coords_y = rink_coord_y / rink_height * image_height
        return image_coords_x, image_coords_y

    # Convert rink coordinates to image coordinates
    x_pixel: List[float] = []
    y_pixel: List[float] = []
    for rink_coord_x, rink_coord_y in rink_coords:
        image_coords_x, image_coords_y = feet_to_pixels(rink_coord_x, rink_coord_y)
        x_pixel.append(image_coords_x + image_length / 2)
        y_pixel.append(image_coords_y + image_height / 2)

    # Create heatmap
    hm, xedges, yedges = np.histogram2d(x_pixel, y_pixel, bins=(100, 100))

    fig = go.Figure()

    # Add heatmap
    fig.add_trace(
        go.Heatmap(
            z=hm.T,
            x=xedges,
            y=yedges,
            colorscale=[
                [0, "rgba(0, 0, 0, 0)"],  # Transparent for zero values
                [
                    0.1,
                    "rgba(255, 255, 255, 0.5)",
                ],  # Semi-transparent white for low values
                [1, "rgba(255, 0, 0, 0.5)"],  # Semi-transparent red for high values
            ],
            opacity=0.5,
        )
    )

    # Add background image
    fig.add_layout_image(
        dict(
            source=image,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=image_length,
            sizey=image_height,
            sizing="stretch",
            opacity=1,
            layer="below",
        )
    )

    if debug_origin:
        fig.add_trace(
            go.Scatter(
                x=[image_length / 2],
                y=[image_height / 2],
                mode="markers",
                marker=dict(color="green", size=10),
                name="Origin",
            )
        )

    # Generate axis labels
    step_size_x = rink_length / 8  # in feet
    step_size_y = rink_height / 4  # in feet

    num_x = int((rink_length / step_size_x) + 1)
    num_y = int((rink_height / step_size_y) + 1)

    xtick_labels = np.linspace(-rink_length / 2, rink_length / 2, num=num_x)
    ytick_labels = np.linspace(-rink_height / 2, rink_height / 2, num=num_y)

    fig.update_xaxes(
        tickvals=np.linspace(0, image_length, num=num_x),
        ticktext=[f"{label:.1f}" for label in xtick_labels],
        title_text="Rink Length (feet)",
    )
    fig.update_yaxes(
        tickvals=np.linspace(0, image_height, num=num_y),
        ticktext=[f"{label:.1f}" for label in ytick_labels],
        title_text="Rink Height (feet)",
    )

    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
    )

    fig.show()
