"""
You can "pre" import stuff in the __init__.py module, but this is not required.
This allows you to import this function as:

    from ift6758.data import get_player_stats

instead of only:

    from ift6758.data.question_1 import get_player_stats

but both are still valid. You can read more about packages and modules here:
https://docs.python.org/3/reference/import.html#regular-packages
"""
from .get_data import retrieve_game_data, game_number_per_year, REGULAR_SEASON, PLAYOFFS
