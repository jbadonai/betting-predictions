import json


class CombinationAnalyzer:
    def __init__(self):
        self.combinations = {}
        self.filename = 'combinations.json'

    def add_combination(self, a, b, c, result):
        self.load_combinations()

        key = (str(a).lower().strip(), str(b).lower().strip(), str(c).lower().strip())
        self.combinations[str(key)] = result
        self.save_combinations()

    def analyze(self, a, b, c):
        self.load_combinations()

        key = (str(a).lower().strip(), str(b).lower().strip(), str(c).lower().strip())
        return self.combinations.get(str(key), "Unknown")

    def save_combinations(self):
        with open(self.filename, 'w') as file:
            json.dump(self.combinations, file)

        self.combinations.clear()

    def load_combinations(self):
        try:
            with open(self.filename, 'r') as file:
                self.combinations = json.load(file)
        except FileNotFoundError:
            with open(self.filename, 'w') as file:
                json.dump(self.combinations, file)

#
# if __name__ == "__main__":
#     analyzer = CombinationAnalyzer()
#
#     # Functionality to add combinations
#     analyzer.add_combination("strong Home", "Weak Home", "Home/Away")
#     analyzer.add_combination("strong Away", "Weak Home", "Home/Away")
#     analyzer.add_combination("strong Home", "Weak Away", "Home/Away")
#     analyzer.add_combination("strong Home", "Strong Home", "Home/Away")
#
#     # Functionality to save combinations to disk
#     analyzer.save_combinations("combinations.json")
#
#     # Functionality to load combinations from disk
#     analyzer.load_combinations("combinations.json")
#
#     # Test analyzing combinations
#     print(analyzer.analyze("strong Home", "Weak Home"))  # Output: Home/Away
#     print(analyzer.analyze("strong Away", "Weak Home"))  # Output: Home/Away
#     print(analyzer.analyze("strong Home", "Weak Away"))  # Output: Home/Away
#     print(analyzer.analyze("strong Home", "Strong Home"))  # Output: Home/Away
