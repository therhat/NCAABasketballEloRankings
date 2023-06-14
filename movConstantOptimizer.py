import pandas as pd
import scipy.optimize as optimize

# read the team names table and initialize elo ratings at 1500
teams = pd.read_excel('teams.xlsx')
elo = pd.Series(1500, index=teams.iloc[:,0], name='Elo')

# read the matchups table
matchups = pd.read_excel('matchups.xlsx')

# define a function to calculate expected result
def expected_result(player_elo, opponent_elo):
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))

# define a function to calculate mean squared error
def mean_squared_error(mov_constants, matchups):
    # set the k-factor and loop through each row in the matchups table
    k = 90
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
        mov_multiplier = ((margin_of_victory + mov_constants[0]) ** mov_constants[1]) / (mov_constants[2] + mov_constants[3] * abs(elo_copy[home_team] - elo_copy[away_team]))

        # update elo ratings based on actual result and margin of victory
        result = row['Result']
        if result == 1:
            home_newelo = elo_copy[home_team] + k * (mov_multiplier * (result - home_xresult))
            away_newelo = elo_copy[away_team] + k * (mov_multiplier * ((1 - result) - away_xresult))
        elif result == 0:
            home_newelo = elo_copy[home_team] + k * (mov_multiplier * (result - home_xresult))
            away_newelo = elo_copy[away_team] + k * (mov_multiplier * ((1 - result) - away_xresult))

        # update elo ratings in the elo series
        elo_copy[home_team] = home_newelo
        elo_copy[away_team] = away_newelo

        # calculate the error between the predicted and actual outcome
        error = (result - home_xresult) ** 2 + ((1 - result) - away_xresult) ** 2
        total_error += error
        n_matches += 1

    # calculate the mean squared error
    mse = total_error / n_matches
    return mse

# define the objective function for optimization
def objective_function(mov_constants):
    return mean_squared_error(mov_constants, matchups)

# define the bounds for the constants and initial guess for optimization
bounds = [(0, 1), (0, 1), (0, 10), (0, 10), (0, 10)]
x0 = [0.5, 0.5, 1, 1, 1]

# run optimization
result = optimize.minimize(fun=objective_function, x0=x0, bounds=bounds)

# print results
print("Optimal values for the constants: ", result.x)
print("Optimal value of the objective function: ", result.fun)
