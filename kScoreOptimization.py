import pandas as pd
import matplotlib.pyplot as plt

# read the team names table and initialize elo ratings at 1500
teams = pd.read_excel('teams.xlsx')
elo = pd.Series(1500, index=teams.iloc[:,0], name='Elo')

# read the matchups table
matchups = pd.read_excel('matchups.xlsx')

# define a function to calculate expected result
def expected_result(player_elo, opponent_elo):
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))

# define a function to calculate mean squared error
def mean_squared_error(k, matchups):
    # set the k-factor and loop through each row in the matchups table
    elo_copy = elo.copy()
    total_error = 0
    n_matches = 0
    for i, row in matchups.iterrows():
        # check if both home team and away team are in the teams table
        home_team = row['Home Team']
        away_team = row['Away Team']
        if home_team not in elo_copy.index or away_team not in elo_copy.index:
            continue

        # calculate xResult for both home team and away team
        home_xresult = expected_result(elo_copy[home_team], elo_copy[away_team])
        away_xresult = expected_result(elo_copy[away_team], elo_copy[home_team])

        # calculate margin of victory multiplier
        margin_of_victory = abs(row['Home Score'] - row['Away Score'])
        mov_multiplier = ((margin_of_victory + 3) ** 0.8) / (7.5 + 0.006 * abs(elo[home_team] - elo[away_team]))
    
        # update elo ratings based on actual result and margin of victory
        result = row['Result']
        if result == 1:
            home_newelo = elo[home_team] + k * (mov_multiplier * (result - home_xresult))
            away_newelo = elo[away_team] + k * (mov_multiplier * ((1 - result) - away_xresult))
        elif result == 0:
            home_newelo = elo[home_team] + k * (mov_multiplier * (result - home_xresult))
            away_newelo = elo[away_team] + k * (mov_multiplier * ((1 - result) - away_xresult))

        # update elo ratings in the elo series copy
        elo_copy[home_team] = home_newelo
        elo_copy[away_team] = away_newelo
        
        # add to total error
        home_error = (home_xresult - result) ** 2
        away_error = (away_xresult - (1 - result)) ** 2
        total_error += home_error + away_error
        n_matches += 2

    # return mean squared error
    return total_error / n_matches

# set up k-score range to test
k_scores = range(70, 100, 1)
errors = []
for k in k_scores:
    error = mean_squared_error(k, matchups)
    errors.append(error)

# plot errors vs k-scores
plt.plot(k_scores, errors)
plt.xlabel('K-Score')
plt.ylabel('Mean Squared Error')
plt.show()

# find index of minimum error
min_error_index = errors.index(min(errors))

# print optimal k-score and its corresponding error
print('Optimal K-Score:', k_scores[min_error_index])
print('Minimum Mean Squared Error:', min(errors))
