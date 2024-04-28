# Provided data
from prettytable import PrettyTable
import numpy as np
from scipy.stats import poisson
import pandas as pd
import Levenshtein


def are_similar_old(string1, string2, threshold=0.3):
    """
    Check if two strings are similar based on Levenshtein distance.

    Args:
    string1 (str): First string.
    string2 (str): Second string.
    threshold (float): Similarity threshold. Default is 0.8.

    Returns:
    bool: True if the strings are similar, False otherwise.
    """
    distance = Levenshtein.distance(string1.lower(), string2.lower())

    max_length = max(len(string1), len(string2))
    similarity = 1 - (distance / max_length)
    return similarity >= threshold


def are_similar(a, b):

    small = None

    if len(a) < len(b):
        small = a
        big = b
    else:
        small = b
        big = a

    big = big.replace("-", " ")
    small = small.replace("-", " ")

    small_list = str(small).split(" ")
    big_list = str(big).split(" ")

    trueCounter = 0
    falseCounter = 0
    for tester in small_list:
        if tester in big_list:
            trueCounter += 1
        else:
            found = False
            if len(tester) > 2:
                for b in big_list:
                    if tester[:-1] == b or b[:-1] == tester:
                        trueCounter += 1
                        found = True
                        break

                if found is True:
                    break
                else:
                    falseCounter += 1

    same = trueCounter > falseCounter
    return same


class FootballPrediction():

    def __init__(self):
        pass

    # def analyze_matches_old(self, data, home_team, away_team):
    #     # Helper function to calculate average
    #     def calculate_average(scores):
    #         return sum(scores) / len(scores) if scores else 0
    #
    #     # Initialize variables
    #     home_wins = away_wins = home_goals = away_goals = 0
    #     home_scores = []
    #     away_scores = []
    #
    #     # Analyze the data
    #     for match in data:
    #         try:
    #             # print(f" team: {match['team']} |home: {match['home']} | away: {match['away']}")
    #             if match['status'] == 'W':
    #                 if match['home'] == home_team and str(match['home_score']).isdigit():
    #                     home_wins += 1
    #                     home_goals += int(match['home_score'])
    #                     home_scores.append(int(match['home_score']))
    #                 elif match['away'] == home_team and str(match['away_score']).isdigit():
    #                     home_wins += 1
    #                     home_goals += int(match['away_score'])
    #                     home_scores.append(int(match['away_score']))
    #                 if match['home'] == away_team and str(match['home_score']).isdigit():
    #                     away_wins += 1
    #                     away_goals += int(match['home_score'])
    #                     away_scores.append(int(match['home_score']))
    #                 elif match['away'] == away_team and str(match['away_score']).isdigit():
    #                     away_wins += 1
    #                     away_goals += int(match['away_score'])
    #                     away_scores.append(int(match['away_score']))
    #         except Exception as e:
    #             print(f"{e}")
    #             print(f"current: team:{match['team']}  - {match['home']}::{match['home_score']}")
    #             print("**************************************************************************")
    #
    #     # Calculate goal difference and average scores
    #
    #     # for match in data:
    #     #     if match['status'] == 'W':
    #     #         # Convert the score to a string before checking if it's a digit
    #     #         home_score = str(match['home_score'])
    #     #         away_score = str(match['away_score'])
    #     #
    #     #         if match['home'] == home_team and home_score.isdigit():
    #     #             home_wins += 1
    #     #             home_goals += int(home_score)
    #     #             home_scores.append(int(home_score))
    #     #         elif match['away'] == home_team and away_score.isdigit():
    #     #             home_wins += 1
    #     #             home_goals += int(away_score)
    #     #             home_scores.append(int(away_score))
    #     #         if match['home'] == away_team and home_score.isdigit():
    #     #             away_wins += 1
    #     #             away_goals += int(home_score)
    #     #             away_scores.append(int(home_score))
    #     #         elif match['away'] == away_team and away_score.isdigit():
    #     #             away_wins += 1
    #     #             away_goals += int(away_score)
    #     #             away_scores.append(int(away_score))
    #
    #     home_goal_diff = home_goals - sum(home_scores)
    #     away_goal_diff = away_goals - sum(away_scores)
    #
    #     home_avg_score = round(calculate_average(home_scores),2)
    #     away_avg_score = round(calculate_average(away_scores),2 )
    #
    #     # Calculate head to head
    #     h2h = None
    #     for match in data:
    #         if {match['home'], match['away']} == {home_team, away_team} and match['status'] == 'W':
    #             h2h = match['home'] if match['home_score'] > match['away_score'] else match['away']
    #
    #     # Calculate team strength
    #     total_wins = home_wins + away_wins
    #     home_strength = round((home_wins / total_wins) * 100 if total_wins else 50)
    #     away_strength = round((away_wins / total_wins) * 100 if total_wins else 50)
    #
    #     # Calculate expected scores (using average scores as a simple method)
    #     expected_home_score = round(home_avg_score * (away_strength / 100),2)
    #     expected_away_score =round(away_avg_score * (home_strength / 100),2)
    #
    #     if round(expected_home_score,1) > round(expected_away_score,1):
    #         winner = "Home"
    #     elif round(expected_home_score,1) < round(expected_away_score,1):
    #         winner = "Away"
    #     else:
    #         winner = "Draw"
    #
    #     if round(expected_home_score) > round(expected_away_score):
    #         winner2 = "Home"
    #     elif round(expected_home_score) < round(expected_away_score):
    #         winner2 = "Away"
    #     else:
    #         winner2 = "Draw"
    #
    #     return f"{home_team} {round(expected_home_score,1)} : {round(expected_away_score,1)} {away_team} |  [{winner}] -  [{winner2}]"
    #
    #     # # Create and populate the table
    #     # table = PrettyTable()
    #     # table.field_names = ["Team", "Wins", "Goal Difference", "Average Scores", "Head to Head", "Team Strength (%)", "Expected Scores"]
    #     # table.add_row([home_team, home_wins, home_goal_diff, home_avg_score, h2h if h2h == home_team else '', home_strength, expected_home_score])
    #     # table.add_row([away_team, away_wins, away_goal_diff, away_avg_score, h2h if h2h == away_team else '', away_strength, expected_away_score])
    #     #
    #     # return table

    def analyze_matches(self, data, home_team, away_team):
        # Helper function to calculate average
        def calculate_average(scores):
            return sum(scores) / len(scores) if scores else 0

        # Initialize variables
        home_wins = away_wins = home_goals = away_goals = 0
        home_scores = []
        away_scores = []

        # Create DataFrame to store match data
        match_df = pd.DataFrame(data)

        # Filter data for relevant matches
        relevant_matches = match_df[match_df['status'] == 'W']

        def check_similarity_home(row):
            return are_similar(row['home'].strip(), home_team) or are_similar(row['away'].strip(), home_team)

        # Function to check similarity for each row
        def check_similarity_away(row):
            return are_similar(row['home'].strip(), away_team) or are_similar(row['away'].strip(), away_team)

        # Apply similarity check and filter relevant matches
        home_matches = relevant_matches[relevant_matches.apply(check_similarity_home, axis=1)]
        away_matches = relevant_matches[relevant_matches.apply(check_similarity_away, axis=1)]

        # Analyze home matches
        for index, match in home_matches.iterrows():
            if str(match['home_score']).isdigit():
                home_wins += 1
                home_goals += int(match['home_score'])
                home_scores.append(int(match['home_score']))
            elif str(match['away_score']).isdigit():
                home_wins += 1
                home_goals += int(match['away_score'])
                home_scores.append(int(match['away_score']))

        # Analyze away matches
        for index, match in away_matches.iterrows():
            if str(match['home_score']).isdigit():
                away_wins += 1
                away_goals += int(match['home_score'])
                away_scores.append(int(match['home_score']))
            elif str(match['away_score']).isdigit():
                away_wins += 1
                away_goals += int(match['away_score'])
                away_scores.append(int(match['away_score']))

        # Calculate goal difference and average scores
        home_goal_diff = home_goals - sum(home_scores)
        away_goal_diff = away_goals - sum(away_scores)

        home_avg_score = round(calculate_average(home_scores), 2)
        away_avg_score = round(calculate_average(away_scores), 2)

        # # Calculate head to head
        # h2h_match = relevant_matches[(relevant_matches['home'].isin([home_team, away_team])) & (
        #     relevant_matches['away'].isin([home_team, away_team]))]


        # Function to check similarity for head to head matches
        def check_similarity_h2h(row):
            return (are_similar(row['home'].strip(), home_team) or are_similar(row['home'].strip(), away_team)) and \
                   (are_similar(row['away'].strip(), home_team) or are_similar(row['away'].strip(), away_team))

        # Apply similarity check and filter head to head matches
        h2h_match = relevant_matches[relevant_matches.apply(check_similarity_h2h, axis=1)]

        # print('HEAD TO HEAD')
        # print(h2h_match.columns)
        # print(h2h_match[['home', 'away', 'home_score', 'away_score']])
        # print()

        h2h_winner = h2h_match.loc[(h2h_match['home_score'] > h2h_match['away_score']), 'home'].values[0] \
            if not h2h_match.empty and h2h_match['home_score'].max() > h2h_match['away_score'].max() else \
            h2h_match.loc[(h2h_match['away_score'] > h2h_match['home_score']), 'away'].values[0] \
                if not h2h_match.empty else None

        # Calculate team strength
        total_wins = home_wins + away_wins
        home_strength = round((home_wins / total_wins) * 100) if total_wins else 50
        away_strength = round((away_wins / total_wins) * 100) if total_wins else 50

        # Calculate expected scores (using average scores as a simple method)
        expected_home_score = round(home_avg_score * (away_strength / 100), 2)
        expected_away_score = round(away_avg_score * (home_strength / 100), 2)

        # Determine winner
        if round(expected_home_score, 1) > round(expected_away_score, 1):
            winner = "Home"
        elif round(expected_home_score, 1) < round(expected_away_score, 1):
            winner = "Away"
        else:
            winner = "Draw"

        if round(expected_home_score) > round(expected_away_score):
            winner2 = "Home"
        elif round(expected_home_score) < round(expected_away_score):
            winner2 = "Away"
        else:
            winner2 = "Draw"

        result_str = f"{home_team} {round(expected_home_score, 1)} : {round(expected_away_score, 1)} {away_team} |  [{winner}] -  [{winner2}]"
        # print(f"Result: {result_str}")
        # input('waiting')
        return result_str

    def analyze_by_poisson_analysis(self, data, home_team, away_team):

        df = pd.DataFrame(data)

        # Filter data for home and away
        home_data = df[df['team'] == home_team]
        away_data = df[df['team'] == away_team]

        # Define the mean goals scored for each team
        home_avg_goals = home_data['home_score'].mean()
        away_avg_goals = away_data['away_score'].mean()

        # Simulate match scores using Poisson distribution
        num_simulations = 100000  # Adjust the number of simulations as needed

        home_home_goals_sim = poisson.rvs(home_avg_goals, size=num_simulations)
        away_away_goals_sim = poisson.rvs(away_avg_goals, size=num_simulations)

        # Calculate average goals from simulations
        home_avg_home_goals_sim = np.mean(home_home_goals_sim)
        away_avg_away_goals_sim = np.mean(away_away_goals_sim)

        # Display the results
        # print(f'{home_team} Average Home Goals (Simulated): {home_avg_home_goals_sim:.2f}')
        # print(f'{away_team} Average Away Goals (Simulated): {away_avg_away_goals_sim:.2f}')
        if round(home_avg_home_goals_sim,1) > round(away_avg_away_goals_sim,1):
            winner = "Home"
        elif round(home_avg_home_goals_sim,1) < round(away_avg_away_goals_sim,1):
            winner = "Away"
        else:
            winner = "Draw"

        if round(home_avg_home_goals_sim) > round(away_avg_away_goals_sim):
            winner2 = "Home"
        elif round(home_avg_home_goals_sim) < round(away_avg_away_goals_sim):
            winner2 = "Away"
        else:
            winner2 = "Draw"

        return f"{home_team} {round(home_avg_home_goals_sim,1)} : {round(away_avg_away_goals_sim,1)} {away_team} |  [{winner}] -  [{winner2}]"

        pass

    def analyze_by_average_goal_scored(self, data, home_team, away_team):
        print('analyzing by average goal scores.....')

        try:
            data = pd.DataFrame(data)
            # print(data)

            # Assuming 'data' is a pandas DataFrame containing your match data
            # Calculate the average home and away goals for each team
            average_home_goals = data.groupby('home')['home_score'].mean()
            average_away_goals = data.groupby('away')['away_score'].mean()

            # print(f"home average score: {average_home_goals} ")
            # print(f"away average score: {average_away_goals} ")


            # Function to get average home goals with similarity check
            def get_average_home_goals(team_name):
                for key in average_home_goals.keys():
                    if are_similar(key, team_name):
                        return average_home_goals[key]
                return 0  # Default value if team_name is not found

            def get_average_away_goals(team_name):
                for key in average_away_goals.keys():
                    if are_similar(key, team_name):
                        return average_away_goals[key]
                return 0  # Default value if team_name is not found

            # Function to calculate expected goals (xG)
            def calculate_xg(home_team, away_team):
                # xG_home = average_home_goals.get(home_team, 0)
                # xG_away = average_away_goals.get(away_team, 0)
                xG_home = get_average_home_goals(home_team)
                xG_away = get_average_away_goals(away_team)

                return xG_home, xG_away

            # Example usage
            print(f"Calculating expected goal for {home_team} and {away_team}")
            xG_home, xG_away = calculate_xg(home_team, away_team)

            print(f"expected golas: {xG_home}, {xG_away}")

            if round(xG_home,1) > round(xG_away,1):
                winner = "Home"
            elif round(xG_home,1) < round(xG_away,1):
                winner = "Away"
            else:
                winner = "Draw"

            if round(xG_home) > round(xG_away):
                winner2 = "Home"
            elif round(xG_home) < round(xG_away):
                winner2 = "Away"
            else:
                winner2 = "Draw"

            return f"{home_team}  {round(xG_home,1)} :  {round(xG_away,1)} {away_team} |  [{winner}] -  [{winner2}]"
        except Exception as e:
            print(f"Inner error at ANALYZE BY AVERAGE GOAL SCORED: {e}")
            pass

# class BasketballPrediction():
#
#     def __init__(self):
#         pass
#
#     def analyze_matches(self, data, home_team, away_team):
#         print('analyzing matches...')
#
#         # Helper function to calculate average
#         def calculate_average(scores):
#             return sum(scores) / len(scores) if scores else 0
#
#         # Initialize variables
#         home_wins = away_wins = home_goals = away_goals = 0
#         home_scores = []
#         away_scores = []
#
#         # Create DataFrame to store match data
#         match_df = pd.DataFrame(data)
#
#         # Filter data for relevant matches
#         relevant_matches = match_df[match_df['status'] == 'W']
#
#         # Function to check similarity for each row
#         def check_similarity_home(row):
#             return are_similar(row['home'].strip(), home_team) or are_similar(row['away'].strip(), home_team)
#
#         # Function to check similarity for each row
#         def check_similarity_away(row):
#             return are_similar(row['home'].strip(), away_team) or are_similar(row['away'].strip(), away_team)
#
#         # Apply similarity check and filter relevant matches
#         home_matches = relevant_matches[relevant_matches.apply(check_similarity_home, axis=1)]
#         away_matches = relevant_matches[relevant_matches.apply(check_similarity_away, axis=1)]
#
#         print('HOME MATCHES:')
#         print(home_matches)
#         print()
#
#         print('AWAY MATCHES')
#         print(away_matches)
#         print()
#
#         # Analyze home matches
#         for match in home_matches.itertuples():
#             home_wins += 1
#             home_goals += match.home_score
#             home_scores.append(match.home_score)
#
#         # Analyze away matches
#         for match in away_matches.itertuples():
#             away_wins += 1
#             away_goals += match.away_score
#             away_scores.append(match.away_score)
#
#         # Calculate goal difference and average scores
#         home_avg_score = round(calculate_average(home_scores), 2)
#         away_avg_score = round(calculate_average(away_scores), 2)
#
#         # Calculate team strength
#         total_wins = home_wins + away_wins
#         home_strength = round((home_wins / total_wins) * 100) if total_wins else 50
#         away_strength = round((away_wins / total_wins) * 100) if total_wins else 50
#
#         # Calculate expected scores (using average scores as a simple method)
#         expected_home_score = round(home_avg_score * (away_strength / 100), 2)
#         expected_away_score = round(away_avg_score * (home_strength / 100), 2)
#
#         # Determine winner
#         if expected_home_score > expected_away_score:
#             winner = "Home"
#         elif expected_home_score < expected_away_score:
#             winner = "Away"
#         else:
#             winner = "Draw"
#
#         result_str = f"{home_team} {round(expected_home_score, 1)} : {round(expected_away_score, 1)} {away_team} | [{winner}]"
#         input('waiting')
#         return result_str
#
#     def analyze_by_poisson_analysis(self, data, home_team, away_team):
#         print('analyzing by poisson analysis....')
#
#         df = pd.DataFrame(data)
#
#         # Filter data for home and away
#         home_data = df[df['team'] == home_team]
#         away_data = df[df['team'] == away_team]
#
#         # Define the mean goals scored for each team
#         home_avg_goals = home_data['away_score'].mean()
#         away_avg_goals = away_data['away_score'].mean()
#
#         # Simulate match scores using Poisson distribution
#         num_simulations = 100000  # Adjust the number of simulations as needed
#
#         home_home_goals_sim = poisson.rvs(home_avg_goals, size=num_simulations)
#         away_away_goals_sim = poisson.rvs(away_avg_goals, size=num_simulations)
#
#         # Calculate average goals from simulations
#         home_avg_home_goals_sim = np.mean(home_home_goals_sim)
#         away_avg_away_goals_sim = np.mean(away_away_goals_sim)
#
#         # Display the results
#         # print(f'{home_team} Average Home Goals (Simulated): {home_avg_home_goals_sim:.2f}')
#         # print(f'{away_team} Average Away Goals (Simulated): {away_avg_away_goals_sim:.2f}')
#         if round(home_avg_home_goals_sim,1) > round(away_avg_away_goals_sim,1):
#             winner = "Home"
#         elif round(home_avg_home_goals_sim,1) < round(away_avg_away_goals_sim,1):
#             winner = "Away"
#         else:
#             winner = "Draw"
#
#         if round(home_avg_home_goals_sim) > round(away_avg_away_goals_sim):
#             winner2 = "Home"
#         elif round(home_avg_home_goals_sim) < round(away_avg_away_goals_sim):
#             winner2 = "Away"
#         else:
#             winner2 = "Draw"
#
#         return f"{home_team} {round(home_avg_home_goals_sim,1)} : {round(away_avg_away_goals_sim,1)} {away_team} |  [{winner}] -  [{winner2}]"
#
#         pass
#
#     def analyze_by_average_goal_scored(self, data, home_team, away_team):
#         try:
#
#             data = pd.DataFrame(data)
#
#             # Assuming 'data' is a pandas DataFrame containing your match data
#             # Calculate the average home and away goals for each team
#             average_home_goals = data.groupby('home')['home_score'].mean()
#             average_away_goals = data.groupby('away')['away_score'].mean()
#
#             # Function to calculate expected goals (xG)
#             def calculate_xg(home_team, away_team):
#                 xG_home = average_home_goals.get(home_team, 0)
#                 xG_away = average_away_goals.get(away_team, 0)
#                 return xG_home, xG_away
#
#             # Example usage
#             xG_home, xG_away = calculate_xg(home_team, away_team)
#             # print(f"Expected Goals for {home_team} (Home): {xG_home}")
#             # print(f"Expected Goals for {away_team} (Away): {xG_away}")
#
#             if round(xG_home,1) > round(xG_away,1):
#                 winner = "Home"
#             elif round(xG_home,1) < round(xG_away,1):
#                 winner = "Away"
#             else:
#                 winner = "Draw"
#
#             if round(xG_home) > round(xG_away):
#                 winner2 = "Home"
#             elif round(xG_home) < round(xG_away):
#                 winner2 = "Away"
#             else:
#                 winner2 = "Draw"
#
#             return f"{home_team}  {round(xG_home,1)} :  {round(xG_away,1)} {away_team} |  [{winner}] -  [{winner2}]"
#         except Exception as e:
#             print(f'An error occurred in ANALYZE BY AVERAGE GOAL SCORED: {e}')
#             input('error inside:')
#             pass



