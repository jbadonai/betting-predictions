#
# # ---------------------------------------
# # ITERATION
# # ---------------------------------------
# #
# # from itertools import product
# #
# # items = ["Strong Home", "Strong Away", "Strong Draw", "Weak Away", "Weak Home"]
# # boxes = 3
# #
# # # Generate all possible combinations
# # possibilities = list(product(items, repeat=boxes))
# #
# # # Print all possibilities
# # for possibility in possibilities:
# #     a, b, c = possibility
# #     print(f"{a},{b},{c}")
#
#
# with open('teamOnlyData.txt', 'r') as f:
#     data = f.read()
#
# with open('oddOnlyData.txt', 'r') as f:
#     data2 = f.read()
#
#
# dataList = data.split("\n\n")
# dataList2 = data2.split("\n\n")
#
# for index, d in enumerate(dataList):
#     nd = d.split("\n")
#     nd2 = dataList2[index].split("\n")
#
#     result = f"{' | '.join(nd)} | {' | '.join(nd2)}"
#     print(result)
#
#
#

from predictionBot import *


bot = PredictionBotMains()
print('starting.l...')
bot.start_bot()
