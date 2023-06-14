import requests
from bs4 import BeautifulSoup
import pandas as pd

# Make a request
url = 'https://www.sports-reference.com/cbb/seasons/men/2023-ratings.html'
response = requests.get(url)

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table with the team information
table = soup.find('table', {'id': 'ratings'})

# Get the table rows
rows = table.find_all('tr')

# Create an empty list to store the data
data = []

# Loop through the rows and extract the team name and conference
for row in rows:
    if row.get('class'):
        continue
        
    team_name_td = row.find('td', {'data-stat': 'school_name'})
    if team_name_td is not None and team_name_td.a is not None:
        team_name = team_name_td.a.text.strip()
    else:
        continue
    
    conference_td = row.find('td', {'data-stat': 'conf_abbr'})
    if conference_td is not None and conference_td.a is not None:
        conference = conference_td.a.text.strip()
    else:
        continue
        
    data.append([team_name, conference])

# Convert the data into a pandas dataframe
df = pd.DataFrame(data, columns=['Team Name', 'Conference'])

# Print the dataframe
print(df.head())

# Save the dataframe to an Excel file
df.to_excel('team_conferences.xlsx', index=False)
