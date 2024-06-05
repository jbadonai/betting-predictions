import pandas as pd
import ast
import re

# code = "302"
dates = input("Filter for which date? :")

# path = rf"C:\Users\ajeyemi.alajede\OneDrive - Emerging Markets Telecommunication Services Limited\Desktop\predictions\{dates}.txt"
path = "fb_result.txt"
extraData = []

with open(path, 'r', encoding='utf-8') as f:
    data = f.read()


def filter(code, data):
    global extraData
    dataList = data.split("\n")
    begin = False

    dataGroup = []

    group = []
    home = None
    away = None
    game_code = None
    accuracy = None

    sporter_counter = 0
    for d in dataList:
        if d.__contains__("Game Time"):
            begin = True

        if d.__contains__("*"):
            begin = False
            continue

        if begin is True:
            if d != "":
                group.append(d)

            # extract home and away team
            if d.__contains__('Teams'):
                home = d.split(":")[1].strip()
                away = d.split(":")[2].strip()

            if d.__contains__("{"):
                sporter_counter += 1
                if sporter_counter == 1:
                    accuracy = d.split(" ")[-1].strip()
                elif sporter_counter == 2:
                    game_code = d.split(" ")[-1].strip()
                    sporter_counter = 0


        if begin is False:
            if len(group) > 0:
                # apply filter

                if str(group).__contains__(f"[{code}]"):

                    x = "\n".join(group)

                    x += "\n\n\t\t\t\t***************************************************\n"
                    dataGroup.append(x)

            extraData.append((home, away, game_code, accuracy))
            group.clear()
            home = None
            away = None
            accuracy = None
            game_code = None
            sporter_counter = 0

    return "\n".join(dataGroup)

codeList = ['302','500','050','410','320','221','113','212','041','203','140','104','311','230','401']

final_filtered_data = ""

print(f"Filtered data for {dates}")
final_filtered_data += f"Filtered data for {dates}\n"
# print()
for code in codeList:
    fd = filter(code, data)
    lb = "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n"

    final_filtered_data += f"{fd}\n{lb}"

with open(f"Filtered/filtered_{dates}.txt", 'w', encoding='utf-8') as f:
    f.write(final_filtered_data)


with open(f"Filtered/extraData_{dates}.txt", 'w', encoding='utf-8') as f:
    f.write(str(extraData))


print('COMPLETED!')

# to excell
#-----------------------

# Read data from the text file
with open(f"Filtered/extraData_{dates}.txt", 'r', encoding='utf-8') as file:
    data = file.read()

# Remove leading and trailing square brackets if present
data = data.strip()[1:-1]

# Split the string into a list of tuples using regular expressions
tuple_strings = re.findall(r'\(([^)]+)\)', data)

# Convert the tuple strings into actual tuples
parsed_data = []
for tuple_str in tuple_strings:
    # Split by comma but ignore commas inside quotes
    items = re.split(r",\s*(?![^()]*\))", tuple_str)
    # Strip quotes and spaces
    items = [item.strip().strip("'") for item in items]
    parsed_data.append(tuple(items))

# Create a DataFrame with the specified headings
df = pd.DataFrame(parsed_data, columns=['home', 'away', 'code', 'accuracy'])
# Save the DataFrame to an Excel file
df.to_excel(f"Filtered/extraData_{dates}.xlsx", index=False)
