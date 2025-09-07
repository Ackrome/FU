import os
import csv
import pickle
from typing import cast

def load_table(filename):
    '''Loads data from file'''
    addition = filename.split('.')[-1]
    if addition=='csv':
        with open(os.path.dirname(os.path.abspath(__file__))+f'\\{filename}', 'r') as csvfile:
            reader = csv.reader(csvfile)
            table = []
            for row in reader:
                table.append(row[0].split(';'))
    elif addition =='pickle':
        with open(filename, 'rb') as f:
            table = pickle.load(f)
    return table

def save_table(data,filename,addition):
    '''Saves data to file with exact addition'''
    if addition == 'pickle':
        with open(filename+addition, 'wb') as f:
            pickle.dump(data, f)
    if addition == 'csv':
        with open(os.path.dirname(os.path.abspath(__file__))+f'\\{filename}.{addition}', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', lineterminator='\n',quotechar='|')
            writer.writerows(data)


def show_files_here(give_list = False):
    files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    if give_list == False: 
        return print("Files in %r: %s" % (os.path.dirname(os.path.abspath(__file__)), files))
    else:
        return(files)
    
    
def get_rows_by_number(table, start, stop=None, copy_table=False):
  """
  Получает таблицу из одной строки или из строк из интервала по номеру строки.

  Args:
    table: Исходная таблица.
    start: Начальный номер строки.
    stop: Конечный номер строки (опционально).
    copy_table: Копировать исходные данные (опционально).

  Returns:
    Таблицу из одной строки или из строк из интервала.
  """
  assert start>stop, 'Начало не может быть больше конца по числовому значению'

  if stop is None:
    stop = start

  if copy_table:
    new_table = table.copy()
  else:
    new_table = table

  new_table = new_table[start:stop+1]

  return new_table

def get_rows_by_index(table, *val1 , copy_table=False):
  """
  Получает новую таблицу из одной строки или из строк со значениями в первом столбце, совпадающими с переданными аргументами val1, ..., valN.

  Args:
    table: Исходная таблица.
    val1, ...: Значения в первом столбце, по которым необходимо выполнить выборку.
    copy_table: Копировать исходные данные (опционально).

  Returns:
    Новую таблицу из одной строки или из строк со значениями в первом столбце, совпадающими с переданными аргументами val1, ..., valN.
  """

  index_list = []
  for val in val1:
    for i in range(len(table)):
      if table[i][0] == val:
        index_list.append(i)

  if index_list == []:
    return None

  if copy_table:
    new_table = table.copy()
  else:
    new_table = table

  result=[]
  result.extend([new_table[i] for i in index_list])

  return result

def get_column_types(table, by_number=True):
  """
  Получает словарь вида «столбец: тип значений».

  Args:
    table: Таблица.
    by_number: Определяет вид значения столбца – целочисленный индекс столбца или его строковое представление.

  Returns:
    Словарь вида «столбец: тип значений».
  """

  column_types = {}
  for i in range(len(table[0])):
    column_type = None
    flag=0
    for row in table:
      if row[i] is None:
        column_type = None
        flag=1
        break
      try:
        int(row[i])
        column_type = int
      except ValueError:
        try:
          float(row[i])
          column_type = float
        except ValueError:
          try:
            str(row[i])
            column_type = str
          except ValueError:
            column_type = bool
    if flag==1:
      break
          
    column_types[0 if i ==0 and by_number==True else by_number and i or table[0][i]] = str(column_type)[8:-2]
  return column_types

def set_column_types(table, types_dict='NOTGIVEN' , by_number=True):
  """
  Задаёт словарь вида «столбец: тип значений».

  Args:
    table: Таблица.
    types_dict: Словарь вида «столбец: тип значений».
    by_number: Определяет вид значения столбца — целочисленный индекс столбца или его строковое представление.

  Raises:
    KeyError: Если в словаре types_dict отсутствует значение для столбца.
    TypeError: Если тип значения в словаре types_dict не является допустимым.
  """
  if types_dict=='NOTGIVEN':
     types_dict=get_column_types(table, by_number)

  if not isinstance(types_dict, dict):
    raise TypeError("types_dict должен быть словарем")

  for column, type_ in types_dict.items():
    if not isinstance(column, (int, str)):
      raise TypeError("Ключ словаря types_dict должен быть целочисленным индексом столбца или его строковым представлением")

    if type_ not in ('int', 'float', 'bool', 'str'):
      raise TypeError("Значение словаря types_dict должно быть допустимым типом")

  if by_number:
    for i, column in enumerate(table[0]):
      if i not in types_dict:
        raise KeyError(f"В словаре types_dict отсутствует значение для столбца с индексом {i}")
      table[i] = [cast(type_, value) for value in table[i]]
  else:
    for column, type_ in types_dict.items():
      if column not in table[0]:
        raise KeyError(f"В словаре types_dict отсутствует значение для столбца с именем {column}")
      table = [
          [cast(type_, value) for value in row] for row in table
      ]
  return table

def get_values(table, column=0):
  """
  Получает список значений (типизированных согласно типу столбца) таблицы из столбца.

  Args:
    table: Таблица.
    column: Столбец, из которого необходимо получить значения.

  Returns:
    Список значений столбца.
  """

  if not isinstance(table, list):
    raise TypeError("table должен быть списком")

  if not isinstance(column, (int, str)):
    raise TypeError("column должен быть целочисленным индексом столбца или его строковым представлением")

  if isinstance(column, int):
    if column < 0 or column >= len(table[0]):
      raise ValueError(f"column должен быть в диапазоне от 0 до {len(table[0]) - 1}")
  else:
    if column not in table[0]:
      raise ValueError(f"column не существует")

  column_type = table[0][column]

  values = []
  for row in table:
    values.append(cast(column_type, row[column]))

  return values

def get_value(table, column=0):
  """
  Получает значение (типизированное согласно типу столбца) таблицы из столбца.

  Args:
    table: Таблица.
    column: Столбец, из которого необходимо получить значение.

  Returns:
    Значение столбца.
  """

  if not isinstance(table, list):
    raise TypeError("table должен быть списком")

  if len(table) != 1:
    raise ValueError("table должен содержать одну строку")

  if not isinstance(column, (int, str)):
    raise TypeError("column должен быть целочисленным индексом столбца или его строковым представлением")

  if isinstance(column, int):
    if column < 0 or column >= len(table[0]):
      raise ValueError(f"column должен быть в диапазоне от 0 до {len(table[0]) - 1}")
  else:
    if column not in table[0]:
      raise ValueError(f"column не существует")

  return cast(table[0][column], table[0][0])

def set_values(table, values, column=0):
  """
  Задаёт список значений values для столбца таблицы.

  Args:
    table: Таблица.
    values: Список значений.
    column: Столбец, для которого необходимо задать значения.

  Returns:
    Таблица с новыми значениями.
  """

  if not isinstance(table, list):
    raise TypeError("table должен быть списком")

  if not isinstance(values, list):
    raise TypeError("values должен быть списком")
  
  if len(table)!=len(values):
    raise ValueError('values должно иметь столько же элментов, сколько строк в таблице')

  if not isinstance(column, (int, str)):
    raise TypeError("column должен быть целочисленным индексом столбца или его строковым представлением")

  if isinstance(column, int):
    if column < 0 or column >= len(table[0]):
      raise ValueError(f"column должен быть в диапазоне от 0 до {len(table[0]) - 1}")
  else:
    if column not in table[0]:
      raise ValueError(f"column не существует")

  column_type = table[0][column]

  for row in table:
    row[column] = cast(column_type, values.pop(0))

  return table

def set_value(table, value, column=0):
  """
  Задаёт значение value для столбца таблицы.

  Args:
    table: Таблица.
    value: Значение.
    column: Столбец, для которого необходимо задать значение.

  Returns:
    Таблица с новым значением.
  """

  if not isinstance(table, list):
    raise TypeError("table должен быть списком")

  if len(table) != 1:
    raise ValueError("table должен содержать одну строку")

  if not isinstance(column, (int, str)):
    raise TypeError("column должен быть целочисленным индексом столбца или его строковым представлением")

  if isinstance(column, int):
    if column < 0 or column >= len(table[0]):
      raise ValueError(f"column должен быть в диапазоне от 0 до {len(table[0]) - 1}")
  else:
    if column not in table[0]:
      raise ValueError(f"column не существует")

  table[0][column] = value

  return table

def print_table(table,length_between=3):
  """
  Красиво выводит таблицу без заголовков, но с учетом максимальной длинны каждого столбца.

  Args:
    table: Таблица.
    length_between: Расстояние между столбцами
  """

  if not isinstance(table, list):
    raise TypeError("table должен быть списком")

  max_lengths = []
  for i in range(len(table[0])):
    max_length = 0
    for row in table:
      if len(str(row[i])) > max_length:
        max_length = len(str(row[i]))
    max_lengths.append(max_length)

  for row in table:
    for column, value in enumerate(row):
      print(f"\033[3{column%7}m{str(value).center(max_lengths[column]+length_between)}\033[0m", end="")
    print()


tabel = load_table('file.csv')

'''print(get_column_types(tabel))
print(set_values(tabel,[1,2,3,4,5,6,7]))
save_table(tabel, 'new', 'csv')'''
print_table(tabel)


