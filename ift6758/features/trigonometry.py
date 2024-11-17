import matplotlib.pyplot as plt
import math

left_net_coords = (-100+11, 0)
right_net_coords = (100-11, 0)

def determine_enemy_net_coords(row):
    event_owner_team = row['eventOwnerTeamId']
    is_event_owner_home_team = row['homeTeam_id'] == event_owner_team
    if is_event_owner_home_team: # pick goal at the opposite side of the owner team
        net_coords = right_net_coords if row['homeTeamDefendingSide'] == "left" else left_net_coords
    else:
        net_coords = left_net_coords if row['homeTeamDefendingSide'] == "left" else right_net_coords
    return net_coords

def compute_distance_from_net(row):
    net_coords = determine_enemy_net_coords(row)
    distance = ((row['xCoord'] - net_coords[0])**2 + row['yCoord']**2)**0.5
    return distance

def compute_angle_from_net(row):
    net_coords = determine_enemy_net_coords(row)
    dx = abs(net_coords[0] - row['xCoord'])
    dy = abs(net_coords[1] - row['yCoord'])
    angle_radian = math.atan2(dy, dx)  
    angle_degrees = math.degrees(angle_radian)  
    return angle_degrees



def plot_distances_histogram(df):
    df['distance_from_net'].hist(bins=50)
    plt.xlabel('Distance from Net (feet)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Distances from Net')
    plt.show()

def plot_angles_histogram(df):
    df['angle_from_net'].hist(bins=50)
    plt.xlabel('Angle from Net (degrees)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Angles from Net')
    plt.show()