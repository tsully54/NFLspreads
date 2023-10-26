import numpy as np
import pandas as pd
import random 
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from PIL import Image
from collections import Counter
import requests

st.title("NFL Spread Analysis")

#load in data from notebook
games = pd.read_csv('games.csv')

#create dataframes by season
season_dfs = {}
for year in games['schedule_season']:
    season_dfs[f'games{year}']= games[games['schedule_season']==year]

st.header("Weekly Averages of Score Totals vs Over/Under Lines")
#plot avg. score totals vs. avg over/under line for last two years
#2023
#calculate average over/under by week
st.subheader("2023")
df23 = season_dfs['games2023']
ou_week23 = pd.DataFrame(df23.groupby('schedule_week')['over_under_line'].mean())
tot_week23 = pd.DataFrame(df23.groupby('schedule_week')['score_total'].mean())
ou_week23['avg_total'] = tot_week23['score_total']

# Create a Matplotlib figure and axis
fig, ax = plt.subplots(figsize=(4, 3))
ax.plot(ou_week23.index, ou_week23['over_under_line'], label='Over/Under 2023', color='blue')
ax.plot(ou_week23.index, ou_week23['avg_total'], label='Average Total 2023', color='red')
ax.set_xlabel('Schedule Week')
ax.set_ylabel('Average')
ax.set_title('Weekly Averages for Over/Under and Score Totals in 2023')
ax.legend()

st.pyplot(fig)
st.subheader("2022")
#2022
#calculate average over/under by week
df22 = season_dfs['games2022']
ou_week22 = pd.DataFrame(df22.groupby('schedule_week')['over_under_line'].mean())
tot_week22 = pd.DataFrame(df22.groupby('schedule_week')['score_total'].mean())
ou_week22['avg_total'] = tot_week22['score_total']

# Create a Matplotlib figure and axis
fig22, ax22 = plt.subplots(figsize=(4, 3))
ax22.plot(ou_week22.index, ou_week22['over_under_line'], label='Over/Under 2022', color='blue')
ax22.plot(ou_week22.index, ou_week22['avg_total'], label='Average Total 2022', color='red')
ax22.set_xlabel('Schedule Week')
ax22.set_ylabel('Average')
ax22.set_title('Weekly Averages for Over/Under and Score Totals in 2022')
ax22.legend()

st.pyplot(fig22)

st.header("Various spread Records for 2023, 2022 and previous 20 years")


################## OVER/UNDERS ##################
# Create an empty dictionary to store the results for each season
season_over_under_results = {}

# Iterate through the dataframes in season_dfs
for year, df in season_dfs.items():
    over_counts = df['over_under_winner'].value_counts()
    over_wins = over_counts[1]
    under_wins = over_counts[0]
    if len(over_counts) >2:
        pushes = over_counts[2]
    else:
        pushes = 0
    
    over_pct = over_wins / (over_wins + under_wins)

    season_over_under_results[year] = (over_wins, under_wins, pushes, over_pct)

# Convert season_over_under_results to a DataFrame
over_under_results = pd.DataFrame(season_over_under_results).T
over_under_results.columns = ['over', 'under', 'pushes', 'over_pct']
over_under_results.index.name = 'Year'
over_under_results.index = [int(year[5:]) for year in over_under_results.index]  # Extracting years
over_under_results = over_under_results[::-1]

# get last 2 seasons and averages
recent_years = over_under_results.loc[[2023,2022]]
over_under_sum = over_under_results.sum()
over_under_df = pd.concat([recent_years, over_under_sum.to_frame().T])
over_under_df.index = ['2023', '2022', 'Last 20 years']
over_under_df['over_pct'] = over_under_df['over'] / (over_under_df['over']+over_under_df['under'])
st.subheader("Over/Unders")
st.dataframe(over_under_df)



################## FAVORITES AGAINST THE SPREAD ##################

#calculate how favorites have done against the spread for each season
season_favorite_results = {}
# Iterate through the dataframes in season_dfs
for year, df in season_dfs.items():
    # Calculate how favorites have done against the spread for the current season
    fav_wins = len(df[df['team_favorite_id'] == df['spread_winner']])
    fav_losses = len(df[df['team_favorite_id'] == df['spread_loser']])
    pushes = len(df[df['spread_winner'] == 'PUSH'])

    season_favorite_results[year] = (fav_wins, fav_losses, pushes)

years = games['schedule_season'].unique()
fav_results_sp = pd.DataFrame(season_favorite_results).T
fav_results_sp.columns = ['win', 'loss', 'push']
fav_results_sp.index = years
fav_results_sp = fav_results_sp[::-1]

# get last 2 seasons and averages
fav_results_sp_2yrs = fav_results_sp.loc[[2023,2022]]
fav_results_sp_sum = fav_results_sp.sum()
fav_results_sp_df = pd.concat([fav_results_sp_2yrs, fav_results_sp_sum.to_frame().T])
fav_results_sp_df.index = ['2023', '2022', 'Last 20 years']
fav_results_sp_df['cover_pct'] = fav_results_sp_df['win'] / (fav_results_sp_df['win']+fav_results_sp_df['loss'])
st.subheader("Favorites against the spread")
st.dataframe(fav_results_sp_df)

################## FAVORITES STRAIGHT UP ##################
# Calculate how favorites have done straight up for each season
season_favorite_results_st = {}

for year, df in season_dfs.items():
    # Calculate how favorites have done straight up for the current season
    fav_wins_st = len(df[df['team_favorite_id'] == df['winner']])
    fav_losses_st = len(df[df['team_favorite_id'] == df['loser']])
    pushes_st = len(df[df['winner'] == 'TIE'])

    season_favorite_results_st[year] = (fav_wins_st, fav_losses_st, pushes_st)

fav_results_st = pd.DataFrame(season_favorite_results_st).T
fav_results_st.columns = ['win', 'loss', 'tie']
fav_results_st.index = years
fav_results_st = fav_results_st[::-1]

fav_results_st_2yrs = fav_results_st.loc[[2023, 2022]]
fav_results_st_sum = fav_results_st.sum()
fav_results_st_df = pd.concat([fav_results_st_2yrs, fav_results_st_sum.to_frame().T])
fav_results_st_df.index = ['2023', '2022', 'Last 20 years']
fav_results_st_df['win_pct'] = fav_results_st_df['win'] / (fav_results_st_df['win'] + fav_results_st_df['loss'])
st.subheader("Favorites Straight Up")
st.dataframe(fav_results_st_df)

################## HOME TEAMS STRAIGHT UP ##################
# Calculate how home teams have done straight up for each season
season_home_results_st = {}

for year, df in season_dfs.items():
    # Calculate how home teams have done straight up for the current season
    home_wins_st = len(df[df['team_home'] == df['winner']])
    home_losses_st = len(df[df['team_home'] == df['loser']])
    home_pushes_st = len(df[df['winner'] == 'TIE'])

    season_home_results_st[year] = (home_wins_st, home_losses_st, home_pushes_st)

home_results_st = pd.DataFrame(season_home_results_st).T
home_results_st.columns = ['win', 'loss', 'tie']
home_results_st.index = years
home_results_st = home_results_st[::-1]

# Get results for the last 2 seasons and calculate the sum
home_results_st_2yrs = home_results_st.loc[[2023, 2022]]
home_results_st_sum = home_results_st.sum()
home_results_st_df = pd.concat([home_results_st_2yrs, home_results_st_sum.to_frame().T])
home_results_st_df.index = ['2023', '2022', 'Last 20 years']
home_results_st_df['win_pct'] = home_results_st_df['win'] / (home_results_st_df['win'] + home_results_st_df['loss'])

st.subheader("Home Teams Straight Up")
st.dataframe(home_results_st_df)

################## HOME TEAMS AGAINST THE SPREAD ##################

# Calculate how home teams have done against the spread for each season
season_home_results_sp = {}

for year, df in season_dfs.items():
    home_wins_sp = 0
    home_losses_sp = 0
    home_ties_sp = 0

    for index, row in df.iterrows():
        if row['team_home'] == row['spread_winner']:
            home_wins_sp += 1
        elif row['team_home'] == row['spread_loser']:
            home_losses_sp += 1

        if row['spread_winner'] == 'PUSH':
            home_ties_sp += 1

    season_home_results_sp[year] = (home_wins_sp, home_losses_sp, home_ties_sp)

home_results_sp = pd.DataFrame(season_home_results_sp).T
home_results_sp.columns = ['win', 'loss', 'push']
home_results_sp.index = years
home_results_sp = home_results_sp[::-1]

# Get results for the last 2 seasons and calculate the sum
home_results_sp_2yrs = home_results_sp.loc[[2023, 2022]]
home_results_sp_sum = home_results_sp.sum()
home_results_sp_df = pd.concat([home_results_sp_2yrs, home_results_sp_sum.to_frame().T])
home_results_sp_df.index = ['2022', '2023', 'Last 20 years']
home_results_sp_df['cover_pct'] = home_results_sp_df['win'] / (home_results_sp_df['win'] + home_results_sp_df['loss'])

st.subheader("Home Teams Against the Spread")
st.dataframe(home_results_sp_df)

################## HOME FAVORITES STRAIGHT UP ##################

# Calculate how home favorites have done straight up for each season
season_home_fav_results_st = {}

for year, df in season_dfs.items():
    home_fav_wins_st = 0
    home_fav_losses_st = 0
    home_fav_ties_st = 0

    for index, row in df.iterrows():
        if row['team_favorite_id'] == row['team_home']:
            if row['team_home'] == row['winner']:
                home_fav_wins_st += 1
            elif row['team_home'] == row['loser']:
                home_fav_losses_st += 1

        if row['team_favorite_id'] == row['team_home']:
            if row['winner'] == 'TIE':
                home_fav_ties_st += 1

    season_home_fav_results_st[year] = (home_fav_wins_st, home_fav_losses_st, home_fav_ties_st)

home_fav_results_st = pd.DataFrame(season_home_fav_results_st).T
home_fav_results_st.columns = ['win', 'loss', 'tie']
home_fav_results_st.index = years
home_fav_results_st = home_fav_results_st[::-1]

# Get results for the last 2 seasons and calculate the sum
home_fav_results_st_2yrs = home_fav_results_st.loc[[2023, 2022]]
home_fav_results_st_sum = home_fav_results_st.sum()
home_fav_results_st_df = pd.concat([home_fav_results_st_2yrs, home_fav_results_st_sum.to_frame().T])
home_fav_results_st_df.index = ['2022', '2023', 'Last 20 years']
home_fav_results_st_df['win_pct'] = home_fav_results_st_df['win'] / (home_fav_results_st_df['win'] + home_fav_results_st_df['loss'])

st.subheader("Home Favorites Straight Up")
st.dataframe(home_fav_results_st_df)

################## HOME FAVORITES AGAINST THE SPREAD ##################

# Calculate how home favorites have done against the spread for each season
season_home_fav_results_sp = {}

for year, df in season_dfs.items():
    home_fav_wins_sp = 0
    home_fav_losses_sp = 0
    home_fav_ties_sp = 0

    for index, row in df.iterrows():
        if row['team_favorite_id'] == row['team_home']:
            if row['team_home'] == row['spread_winner']:
                home_fav_wins_sp += 1
            elif row['team_home'] == row['spread_loser']:
                home_fav_losses_sp += 1

        if row['team_favorite_id'] == row['team_home']:
            if row['spread_winner'] == 'PUSH':
                home_fav_ties_sp += 1

    season_home_fav_results_sp[year] = (home_fav_wins_sp, home_fav_losses_sp, home_fav_ties_sp)

home_fav_results_sp = pd.DataFrame(season_home_fav_results_sp).T
home_fav_results_sp.columns = ['win', 'loss', 'push']
home_fav_results_sp.index = years
home_fav_results_sp = home_fav_results_sp[::-1]

# Get results for the last 2 seasons and calculate the sum
home_fav_results_sp_2yrs = home_fav_results_sp.loc[[2023, 2022]]
home_fav_results_sp_sum = home_fav_results_sp.sum()
home_fav_results_sp_df = pd.concat([home_fav_results_sp_2yrs, home_fav_results_sp_sum.to_frame().T])
home_fav_results_sp_df.index = ['2022', '2023', 'Last 20 years']
home_fav_results_sp_df['cover_pct'] = home_fav_results_sp_df['win'] / (home_fav_results_sp_df['win'] + home_fav_results_sp_df['loss'])

st.subheader("Home Favorites Against the Spread")
st.dataframe(home_fav_results_sp_df)

################## HOME UNDERDOGS STRAIGHT UP ##################

# Calculate how home underdogs have done straight up for each season
season_home_dog_results_st = {}

for year, df in season_dfs.items():
    home_dog_wins_st = 0
    home_dog_losses_st = 0
    home_dog_ties_st = 0

    for index, row in df.iterrows():
        if row['team_favorite_id'] == row['team_away']:
            if row['team_home'] == row['winner']:
                home_dog_wins_st += 1
            elif row['team_home'] == row['loser']:
                home_dog_losses_st += 1

        if row['team_favorite_id'] == row['team_away']:
            if row['winner'] == 'TIE':
                home_dog_ties_st += 1

    season_home_dog_results_st[year] = (home_dog_wins_st, home_dog_losses_st, home_dog_ties_st)

home_dog_results_st = pd.DataFrame(season_home_dog_results_st).T
home_dog_results_st.columns = ['win', 'loss', 'tie']
home_dog_results_st.index = years
home_dog_results_st = home_dog_results_st[::-1]

# Get results for the last 2 seasons and calculate the sum
home_dog_results_st_2yrs = home_dog_results_st.loc[[2023, 2022]]
home_dog_results_st_sum = home_dog_results_st.sum()
home_dog_results_st_df = pd.concat([home_dog_results_st_2yrs, home_dog_results_st_sum.to_frame().T])
home_dog_results_st_df.index = ['2022', '2023', 'Last 20 years']
home_dog_results_st_df['win_pct'] = home_dog_results_st_df['win'] / (home_dog_results_st_df['win'] + home_dog_results_st_df['loss'])

st.subheader("Home Underdogs Straight Up")
st.dataframe(home_dog_results_st_df)


################## HOME UNDERDOGS AGAINST THE SPREAD ##################
# Calculate how home teams have done against the spread for each season
season_home_dog_results_sp = {}

for year, df in season_dfs.items():
    home_dog_wins_sp = 0
    home_dog_losses_sp = 0
    home_dog_ties_sp = 0

    for index, row in df.iterrows():
        if row['team_favorite_id'] == row['team_away']:
            if row['team_home'] == row['spread_winner']:
                home_dog_wins_sp += 1
            elif row['team_home'] == row['spread_loser']:
                home_dog_losses_sp += 1

        if row['team_favorite_id'] == row['team_away']:
            if row['spread_winner'] == 'PUSH':
                home_dog_ties_sp += 1

    season_home_dog_results_sp[year] = (home_dog_wins_sp, home_dog_losses_sp, home_dog_ties_sp)

home_dog_results_sp = pd.DataFrame(season_home_dog_results_sp).T
home_dog_results_sp.columns = ['win', 'loss', 'tie']
home_dog_results_sp.index = years
home_dog_results_sp = home_dog_results_sp[::-1]

# Get results for the last 2 seasons and calculate the sum
home_dog_results_sp_2yrs = home_dog_results_sp.loc[[2023, 2022]]
home_dog_results_sp_sum = home_dog_results_sp.sum()
home_dog_results_sp_df = pd.concat([home_dog_results_sp_2yrs, home_dog_results_sp_sum.to_frame().T])
home_dog_results_sp_df.index = ['2023', '2022', 'Last 20 years']
home_dog_results_sp_df['cover_pct'] = home_dog_results_sp_df['win'] / (home_dog_results_sp_df['win'] + home_dog_results_sp_df['loss'])

st.subheader("Home Underdogs Against the Spread")
st.dataframe(home_dog_results_sp_df)
