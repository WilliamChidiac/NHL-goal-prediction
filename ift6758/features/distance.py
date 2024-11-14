import matplotlib.pyplot as plt


left_goal_coords = (-100+11, 0)
right_goal_coords = (100-11, 0)

def compute_distance(row):
    event_owner_team = row['eventOwnerTeamId']
    is_event_owner_home_team = row['homeTeam_id'] == event_owner_team
    if is_event_owner_home_team: # pick goal at the opposite side of the owner team
        goal_coords = right_goal_coords if row['homeTeamDefendingSide'] == "left" else left_goal_coords
    else:
        goal_coords = left_goal_coords if row['homeTeamDefendingSide'] == "left" else right_goal_coords
    distance = ((row['xCoord'] - goal_coords[0])**2 + row['yCoord']**2)**0.5
    return distance

def plot_histogram(df):
    df['distance_from_goal'].hist(bins=50)
    plt.xlabel('Distance from Goal')
    plt.ylabel('Frequency')
    plt.title('Histogram of Distances from Goal')
    plt.show()