import PySimpleGUI as sg

layout = [[sg.Button(f'{row}, {col}') for col in range(4)] for row in range(4)]
event, values = sg.Window('List Comprehensions', layout).read(close=False)