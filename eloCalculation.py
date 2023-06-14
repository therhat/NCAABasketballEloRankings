import pandas as pd

# read the team names table and initialize elo ratings at 1500
teams = pd.read_excel('teams.xlsx')
elo = pd.Series(1500, index=teams.iloc[:,0], name='Elo')

# read the matchups table
matchups = pd.read_excel('matchups.xlsx')

# set the k-factor and home court advantage constant
k = 20
HCA = 100

# loop through each row in the matchups table
for i, row in matchups.iterrows():
    # check if both home team and away team are in the teams table
    home_team = row['Home Team']
    away_team = row['Away Team']
    if home_team not in elo.index or away_team not in elo.index:
        continue

    # calculate home court advantage based on the Neutral column of the matchups table
    if row['Neutral'] == 1:
        home_hca = 0
        away_hca = 0
    else:
        home_hca = HCA
        away_hca = 0

    # calculate xResult for both home team and away team
    home_xresult = 1 / (1 + 10 ** ((elo[away_team] - elo[home_team] + home_hca) / 400))
    away_xresult = 1 / (1 + 10 ** ((elo[home_team] - elo[away_team] + home_hca) / 400))

    # calculate margin of victory multiplier
    margin_of_victory = abs(row['Home Score'] - row['Away Score'])
    mov_multiplier = ((margin_of_victory + 3) ** 0.8) / (7.5 + 0.006 * abs(elo[home_team] - elo[away_team] + home_hca - away_hca))

    # update elo ratings based on actual result and margin of victory
    result = row['Result']
    if result == 1:
        home_newelo = elo[home_team] + k * (mov_multiplier * (result - home_xresult))
        away_newelo = elo[away_team] + k * (mov_multiplier * ((1 - result) - away_xresult))
    elif result == 0:
        home_newelo = elo[home_team] + k * (mov_multiplier * (result - home_xresult))
        away_newelo = elo[away_team] + k * (mov_multiplier * ((1 - result) - away_xresult))

    # update elo ratings in the elo series
    elo[home_team] = home_newelo
    elo[away_team] = away_newelo

# print the resulting table of team names and their Elo ratings
print(elo.to_frame().round())

# create a dataframe of team names and Elo ratings
team_elo_df = elo.to_frame().round()

# save the dataframe as an Excel file named "teamElo.xlsx"
team_elo_df.to_excel("teamElo.xlsx")
