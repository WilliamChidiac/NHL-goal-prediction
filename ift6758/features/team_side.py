import pandas as pd
from tqdm import tqdm

def determine_home_team_defending_side_offensive_event(event_row):
    if event_row['zoneCode'] != 'O':
        print("input has to be offensive zone event")
        return None
    team_id = event_row["eventOwnerTeamId"]
    home_team_id = event_row["homeTeam_id"]
    x_coord = event_row["xCoord"]

    if x_coord > 0 and team_id == home_team_id:
        return "left"
    elif x_coord < 0 and team_id == home_team_id:
        return "right"
    elif x_coord > 0 and team_id != home_team_id:
        return "right"
    elif x_coord < 0 and team_id != home_team_id:
        return "left"
    
def determine_home_team_defending_side_defensive_event(event_row):
    if event_row['zoneCode'] != 'D':
        print("input has to be offensive zone event")
        return None
    team_id = event_row["eventOwnerTeamId"]
    home_team_id = event_row["homeTeam_id"]
    x_coord = event_row["xCoord"]

    if x_coord > 0 and team_id == home_team_id:
        return "right"
    elif x_coord < 0 and team_id == home_team_id:
        return "left"
    elif x_coord > 0 and team_id != home_team_id:
        return "left"
    elif x_coord < 0 and team_id != home_team_id:
        return "right"
    


def populate_home_team_defending_side(game_id, period_number, df, home_team_defending_side_dict, home_team_defending_side_not_found, home_team_defending_side_mismatches):
    # filter for offensive zone events in the period of the game
    game_period_df_offensive = df[(df['id'] == game_id) & (df['periodDescriptor_number'] == period_number) & (df['zoneCode'] == 'O')]
    game_period_df_defensive = df[(df['id'] == game_id) & (df['periodDescriptor_number'] == period_number) & (df['zoneCode'] == 'D')]


    if len(game_period_df_offensive) == 0 and len(game_period_df_defensive) == 0: # overtime periods may have no offensive zone events
        print("no offensive or defensive zone event found in period")
        print("game_id: ", game_id, "period_number: ", period_number)
        home_team_defending_side_not_found.append((game_id, period_number))
        return None
    
    defending_side = None
    if len(game_period_df_offensive) > 0:
        event = game_period_df_offensive.iloc[0] # take the first offensive zone event in the period
        defending_side = determine_home_team_defending_side_offensive_event(event)
    elif len(game_period_df_defensive) > 0:
        event = game_period_df_defensive.iloc[0]
        defending_side = determine_home_team_defending_side_defensive_event(event)

    if pd.notna(event["homeTeamDefendingSide"]) and defending_side: # sanity check with existing homeDefendingSides
        if event["homeTeamDefendingSide"] != defending_side:
            # print(event["homeTeamDefendingSide"])
            # print("defending side mismatch", defending_side)
            # print("game id", game_id)
            # print("period number", period_number)
            home_team_defending_side_mismatches.append((game_id, period_number))
               

    if defending_side: # do not overwrite if no defending side is found
        home_team_defending_side_dict[f"{game_id}_{period_number}"]= defending_side
    else:
        home_team_defending_side_not_found.append((game_id, period_number))
    
    
def update_home_team_defending_side(df, home_team_defending_side_dict):
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        key = f"{row['id']}_{row['periodDescriptor_number']}"
        if key in home_team_defending_side_dict:
            df.at[index, 'homeTeamDefendingSide'] = home_team_defending_side_dict[key]
    return df
