import os
import re
import argparse
from collections import defaultdict
from typing import List, Tuple


class Occurrence:
    def __init__(self, file_path, line, occurrence):
        self.file = file_path
        self.line: int = line
        self.occurrence = occurrence.replace(';', '')

    def __str__(self):
        return f"{self.occurrence} line {self.line} in {self.file}"


def find_duplicates(occurrences: List[Occurrence]) -> List[Tuple[Occurrence, Occurrence]]:
    # Словарь для хранения списков по значению occurrence
    occurrence_dict = defaultdict(list)

    # Заполняем словарь
    for occ in occurrences:
        occurrence_dict[occ.occurrence].append(occ)

    # Список для хранения кортежей совпадающих объектов
    duplicates = []

    # Проходим по словарю и создаем кортежи для совпадающих значений
    for occ_list in occurrence_dict.values():
        if len(occ_list) > 1:
            for i in range(len(occ_list)):
                for j in range(i + 1, len(occ_list)):
                    duplicates.append((occ_list[i], occ_list[j]))

    return duplicates


def find_concepts_and_nrels(directory):
    # Паттерн для поиска соответствующих строк
    pattern = re.compile(r"^[ ]*concept_\w+$|^nrel_[\w]+")

    # Список для хранения всех совпадений
    matches = []

    # Проход по всем файлам в указанной директории
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Обработка только файлов с расширением .scs
            if file.endswith('.scs'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        line = line.strip()
                        # Поиск совпадений в строке
                        if pattern.match(line):
                            matches.append(Occurrence(file_path, i+1, line))

    return matches


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="путь к директории с файлами .scs")
    parser.add_argument("--all", action="store_true", help="--all для вывода всех идентификаторов")
    args = parser.parse_args()

    directory = args.directory
    print(directory)

    matches = find_concepts_and_nrels(directory)

    didi = {}
    for i1, i2 in find_duplicates(matches):
        occurrence = i1.occurrence  # Extract the occurrence from i1

        if occurrence not in didi:
            didi[occurrence] = set()

        didi[occurrence].add(i1)
        didi[occurrence].add(i2)

    if args.all:
        for i in matches:
            occurrence = i.occurrence
            if occurrence not in didi:
                didi[occurrence] = set()
            didi[occurrence].add(i)

    for key, value in didi.items():
        value_str = '\033[32m'
        for count, i in enumerate(value):
            if count == 0:
                value_str += '\033[32m'
            else:
                value_str += '\033[31m'

            value_str += f"\n\t|line {i.line}: {i.file}\033[0m"

        print(f"\033[1m{key}\033[0m : {value_str}")

    # for i1, i2 in find_duplicates(matches):
    #     print(f"\033[1m{i1.occurrence}\033[0m |line {i1.line}: \033[32m{i1.file}\033[0m -- |line {i2.line}: \033[31m{i2.file}\033[0m")
