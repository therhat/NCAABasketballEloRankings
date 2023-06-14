import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta
import time

# specify the URL template for the website to scrape
url_template = "https://www.sports-reference.com/cbb/boxscores/index.cgi?month={month}&day={day}&year={year}"

# specify the range of dates to scrape (inclusive)
start_date = date(2022, 11, 7)
end_date = date(2023, 4, 2)

# create an empty list to store the scraped data
data = []

# read the neutral site matchups table into a dataframe
matchups_df = pd.read_excel('neutralSiteMatchups.xlsx')

# loop through each date in the range of dates
current_date = start_date
while current_date <= end_date:
    # generate the URL for the current date
    url = url_template.format(month=current_date.month, day=current_date.day, year=current_date.year)

    # send a GET request to the website
    response = requests.get(url)

    # create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # find the div tag with the class 'game_summaries'
    game_summaries = soup.find('div', {'class': 'game_summaries'})

    # if there are no matchups for this date, skip to the next date
    if game_summaries is None:
        current_date += timedelta(days=1)
        continue

    # loop through each child div inside the game_summaries div
    for matchup in game_summaries.find_all('div', {'class': 'game_summary nohover gender-m'}):
        # extract the away team name and score
        away_team = matchup.find('tr').find('td').find('a').text
        away_score = matchup.find('tr').find_all('td')[1].text
        # extract the home team name and score
        home_team = matchup.find_all('tr')[1].find('td').find('a').text
        home_score = matchup.find_all('tr')[1].find_all('td')[1].text
        # determine if the matchup was played at a neutral site
        neutral = 0
        # check if the game summary has a third row with text other than "Men's"
        if len(matchup.find_all('tr')) > 2:
            third_row_text = matchup.find_all('tr')[2].find('td').text
            if third_row_text and third_row_text != "Men's":
                neutral = 1
        # determine the result based on which team has the higher score
        if home_score == '':
            result = 'nan'
        elif int(home_score) > int(away_score):
            result = 1
        else:
            result = 0
        # add the extracted data to the list
        if result != 'nan':
            data.append({
                'Date': current_date.strftime('%m/%d/%Y'),
                'Home Team': home_team,
                'Away Team': away_team,
                'Home Score': home_score,
                'Away Score': away_score,
                'Result': result,
                'Neutral': neutral
            })
    # increment the current date by one day
    current_date += timedelta(days=1)
    
    # wait for 3 seconds to avoid jail
    time.sleep(3.1)
    
# loop through the matchups and update the Neutral flag if the matchup is in the neutral site table
for matchup in data:
    matchups_df = pd.read_excel('neutralSiteMatchups.xlsx')
    neutral_matchup = matchups_df.loc[(matchups_df['Date'] == matchup['Date'])
                                      & (matchups_df['Home Team'] == matchup['Home Team'])
                                      & (matchups_df['Away Team'] == matchup['Away Team'])]
    if not neutral_matchup.empty:
        matchup['Neutral'] = 1

# create a DataFrame from the scraped data
df = pd.DataFrame(data)

# print the DataFrame
print(df)

# Save the dataframe to an Excel file
df.to_excel('matchups.xlsx', index=False)
