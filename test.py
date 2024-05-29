data = """
     Game Time:      [ 00:00 ]
                                   Teams:          CSD San Martin  :  Argentino de Quilmes
                                   Prediction:     ['H', 'H', 'H', 'H', 'D']
                                   Accuracy:       [45.75, 36.6, 37.91, 44.44, 41.83]
                                   Summary:        {'H': 41, 'D': 42}  [83]
                                                   {'H': 4, 'D': 1} [401]
                                                   H/D  [Home or Draw [1X]]
                                   ********************************************************************************
                                   
                                   Game Time:      [ 00:15 ]
                                   Teams:          Trem AP  :  Rio Branco FC AC
                                   Prediction:     ['H', 'H', 'H', 'H', 'H']
                                   Accuracy:       [45.75, 39.22, 39.87, 44.44, 41.83]
                                   Summary:        {'H': 42}  [42]
                                                   {'H': 5} [500]
                                                   H/D  [Home or Draw [1X]]
                                   ********************************************************************************
                                   
                                   Game Time:      [ 01:00 ]
                                   Teams:          Atletico Tucuman  :  CA Platense
                                   Prediction:     ['H', 'D', 'D', 'H', 'D']
                                   Accuracy:       [45.75, 36.6, 40.52, 44.44, 41.83]
                                   Summary:        {'H': 45, 'D': 40}  [85]
                                                   {'H': 2, 'D': 3} [203]
                                                   H/D  [Home or Draw [1X]]
                                   ********************************************************************************
                                   
                                   Game Time:      [ 01:00 ]
                                   Teams:          Botafogo FC SP  :  Gremio Novorizontino SP
                                   Prediction:     ['D', 'D', 'H', 'H', 'D']
                                   Accuracy:       [45.75, 38.56, 37.91, 44.44, 41.83]
                                   Summary:        {'H': 41, 'D': 42}  [83]
                                                   {'D': 3, 'H': 2} [203]
                                                   H/D  [Home or Draw [1X]]
                                                   
                                        *******************************************************************************
"""

path = r"C:\Users\ajeyemi.alajede\OneDrive - Emerging Markets Telecommunication Services Limited\Desktop\predictions\27.txt"


path = "fb_result.txt"
with open(path, 'r', encoding='utf-8') as f:
    data = f.read()

def filter(code, data):
    dataList = data.split("\n")
    begin = False

    dataGroup = []
    group = []
    for d in dataList:
        if d.__contains__("Game Time"):
            begin = True

        if d.__contains__("*"):
            begin = False
            continue

        if begin is True:
            if d != "":
                group.append(d)

        if begin is False:
            if len(group) > 0:
                # apply filter

                if str(group).__contains__(f"[{code}]"):

                    x = "\n".join(group)

                    x += "\n\n\t\t\t\t\t\t\t\t\t***************************************************\n"
                    dataGroup.append(x)
            group.clear()

    return "\n".join(dataGroup)


print(filter('500', data))