# Provided data
from prettytable import PrettyTable

class FootballPrediction():

    def __init__(self):
        pass

    def analyze_matches(self, data, home_team, away_team):
        # Helper function to calculate average
        def calculate_average(scores):
            return sum(scores) / len(scores) if scores else 0

        # Initialize variables
        home_wins = away_wins = home_goals = away_goals = 0
        home_scores = []
        away_scores = []

        # Analyze the data
        for match in data:
            try:
                # print(f" team: {match['team']} |home: {match['home']} | away: {match['away']}")
                if match['status'] == 'W':
                    if match['home'] == home_team and str(match['home_score']).isdigit():
                        home_wins += 1
                        home_goals += int(match['home_score'])
                        home_scores.append(int(match['home_score']))
                    elif match['away'] == home_team and str(match['away_score']).isdigit():
                        home_wins += 1
                        home_goals += int(match['away_score'])
                        home_scores.append(int(match['away_score']))
                    if match['home'] == away_team and str(match['home_score']).isdigit():
                        away_wins += 1
                        away_goals += int(match['home_score'])
                        away_scores.append(int(match['home_score']))
                    elif match['away'] == away_team and str(match['away_score']).isdigit():
                        away_wins += 1
                        away_goals += int(match['away_score'])
                        away_scores.append(int(match['away_score']))
            except Exception as e:
                print(f"{e}")
                print(f"current: team:{match['team']}  - {match['home']}::{match['home_score']}")
                print("**************************************************************************")

        # Calculate goal difference and average scores

        # for match in data:
        #     if match['status'] == 'W':
        #         # Convert the score to a string before checking if it's a digit
        #         home_score = str(match['home_score'])
        #         away_score = str(match['away_score'])
        #
        #         if match['home'] == home_team and home_score.isdigit():
        #             home_wins += 1
        #             home_goals += int(home_score)
        #             home_scores.append(int(home_score))
        #         elif match['away'] == home_team and away_score.isdigit():
        #             home_wins += 1
        #             home_goals += int(away_score)
        #             home_scores.append(int(away_score))
        #         if match['home'] == away_team and home_score.isdigit():
        #             away_wins += 1
        #             away_goals += int(home_score)
        #             away_scores.append(int(home_score))
        #         elif match['away'] == away_team and away_score.isdigit():
        #             away_wins += 1
        #             away_goals += int(away_score)
        #             away_scores.append(int(away_score))

        home_goal_diff = home_goals - sum(home_scores)
        away_goal_diff = away_goals - sum(away_scores)

        home_avg_score = round(calculate_average(home_scores),2)
        away_avg_score = round(calculate_average(away_scores),2 )

        # Calculate head to head
        h2h = None
        for match in data:
            if {match['home'], match['away']} == {home_team, away_team} and match['status'] == 'W':
                h2h = match['home'] if match['home_score'] > match['away_score'] else match['away']

        # Calculate team strength
        total_wins = home_wins + away_wins
        home_strength = round((home_wins / total_wins) * 100 if total_wins else 50)
        away_strength = round((away_wins / total_wins) * 100 if total_wins else 50)

        # Calculate expected scores (using average scores as a simple method)
        expected_home_score = round(home_avg_score * (away_strength / 100),2)
        expected_away_score =round(away_avg_score * (home_strength / 100),2)

        # Create and populate the table
        table = PrettyTable()
        table.field_names = ["Team", "Wins", "Goal Difference", "Average Scores", "Head to Head", "Team Strength (%)", "Expected Scores"]
        table.add_row([home_team, home_wins, home_goal_diff, home_avg_score, h2h if h2h == home_team else '', home_strength, expected_home_score])
        table.add_row([away_team, away_wins, away_goal_diff, away_avg_score, h2h if h2h == away_team else '', away_strength, expected_away_score])

        return table

