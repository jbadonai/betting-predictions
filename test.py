from itertools import product

items = ["Strong Home", "Strong Away", "Strong Draw", "Weak Away", "Weak Home"]
boxes = 3

# Generate all possible combinations
possibilities = list(product(items, repeat=boxes))

# Print all possibilities
for possibility in possibilities:
    a, b, c = possibility
    print(f"{a},{b},{c}")