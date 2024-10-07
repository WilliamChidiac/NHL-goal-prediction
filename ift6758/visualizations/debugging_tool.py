from PIL import Image
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from ift6758.data import get_data

# Load the image
rink_image_path = "../figures/nhl_rink.png"
rink_image = Image.open(rink_image_path)


def plot_coords_on_image(
    rink_coord_x, rink_coord_y, image=rink_image, debug_origin=False
) -> None:

    # Get dimensions
    image_length, image_height = image.size
    rink_length = 200
    rink_height = 85

    def feet_to_pixels(rink_coord_x, rink_coord_y):

        image_coords_x = rink_coord_x / rink_length * image_length
        image_coords_y = rink_coord_y / rink_height * image_height

        return image_coords_x, image_coords_y

    # Convert to pixel coordinates
    image_coords_x, image_coords_y = feet_to_pixels(rink_coord_x, rink_coord_y)

    # Display the image with the point

    _, ax = plt.subplots()
    ax.imshow(image)

    ax.invert_yaxis()

    if debug_origin:
        origin_x, origin_y = 0, 0
        adjusted_origin_x = origin_x + image_length / 2
        adjusted_origin_y = origin_y + image_height / 2
        ax.plot(origin_x, origin_y, "bo")
        ax.plot(adjusted_origin_x, adjusted_origin_y, "go")

    # Adjust coordinates to center origin
    adjusted_coords_x = image_coords_x + image_length / 2
    adjusted_coords_y = image_coords_y + image_height / 2

    # Plot the point with the adjusted coordinates
    ax.plot(
        adjusted_coords_x,
        adjusted_coords_y,
        "o",
        markersize=10,
        markerfacecolor="magenta",
    )

    # Generate axis labels
    step_size_x = rink_length / 8  # in feet
    step_size_y = rink_height / 4  # in feet

    num_x = int((rink_length / step_size_x) + 1)
    num_y = int((rink_height / step_size_y) + 1)

    xtick_labels = np.linspace(-rink_length / 2, rink_length / 2, num=num_x)
    ytick_labels = np.linspace(-rink_height / 2, rink_height / 2, num=num_y)

    ax.set_xticks(np.linspace(0, image_length, num=num_x))
    ax.set_yticks(np.linspace(0, image_height, num=num_y))

    ax.set_xticklabels([f"{label:.1f}" for label in xtick_labels])
    ax.set_yticklabels([f"{label:.1f}" for label in ytick_labels])
    ax.set_xlabel("Rink Length (feet)")
    ax.set_ylabel("Rink Height (feet)")

    # Invert the y-axis to match the image coordinate system

    plt.show()


def print_game_info(game_data):
    # TODO: display the sides of the team depending on the period (problem: HomeTeamDefendingSide available from 2019 only)
    print("id", game_data["id"])
    print("date", game_data["gameDate"])
    print("Venue Location: ", game_data["venueLocation"]["default"])
    print("Home Team: ", game_data["homeTeam"]["name"]["default"])
    print("Away Team:", game_data["awayTeam"]["name"]["default"])
    print()


def print_event_info(event):
    print("event id: ", event["eventId"])
    print("event description: ", event["typeDescKey"])
    if "details" in event:
        if "xCoord" in event["details"] and "yCoord" in event["details"]:
            print("x: ", event["details"]["xCoord"], "y: ", event["details"]["yCoord"])
            plot_coords_on_image(
                event["details"]["xCoord"],
                event["details"]["yCoord"],
                debug_origin=False,
            )
        else:
            print("No coordinates available")


def display_regular_season(season: str):
    def on_game_id_change(change):
        game_id = f"{season}{get_data.REGULAR_SEASON}{change['new']:04d}"
        data = get_data.retrieve_game_data(game_id)

        clear_output(wait=True)
        if data is None:
            print(f"Game ID {game_id} doesn't exist")
            clear_output(wait=True)
            display(game_id_slider)
            return

        display(game_id_slider)  # Re-display the IntSlider widget
        print_game_info(data)

        events = data["plays"]
        event_slider = widgets.IntSlider(
            min=0, max=len(events), step=1, description="Event no:"
        )  # event number is the index in the list of events
        display(event_slider)

        def on_event_id_change(change):
            event = events[change["new"]]
            clear_output(wait=True)

            display(game_id_slider)
            print_game_info(data)
            display(event_slider)
            print_event_info(event)

        event_slider.observe(on_event_id_change, names="value")

    game_number = int(get_data.game_number_per_year[season])
    game_id_slider = widgets.IntSlider(
        min=1, max=game_number, step=1, description="Game ID:"
    )

    game_id_slider.observe(on_game_id_change, names="value")
    display(game_id_slider)


def print_playoff_game_info(game_id):
    _, round, matchup, game = game_id.split("_")[2].split("-")
    print(f"Round: {round}")
    print(f"Matchup: {matchup}")
    print(f"Game: {game}")
    print()


def display_playoff_season(season: str):

    def on_game_id_change(change):
        game_id = change["new"]
        clean_game_id = get_data.clean_playoff_game_id(game_id)
        data = get_data.retrieve_game_data(clean_game_id)
        clear_output(wait=True)

        if data is None:
            print(f"Game ID {game_id} doesn't exist")
            display(team_dropdown)
            return

        display(team_dropdown)  # Re-display the dropdown widget

        print_game_info(data)
        print_playoff_game_info(game_id)

        events = data["plays"]
        event_slider = widgets.IntSlider(
            min=0, max=len(events), step=1, description="Event no:"
        )  # event number is the index in the list of events
        display(event_slider)

        def on_event_id_change(change):
            event = events[change["new"]]
            clear_output(wait=True)

            display(team_dropdown)
            print_game_info(data)
            display(event_slider)
            print_event_info(event)

        event_slider.observe(on_event_id_change, names="value")

    playoff_game_ids = get_data.playoff_game_id_generator(season)

    team_dropdown = widgets.Dropdown(
        options=playoff_game_ids,  # Example teams
        value=None,
        description="Game id:",
    )
    display(team_dropdown)
    team_dropdown.observe(on_game_id_change, names="value")
