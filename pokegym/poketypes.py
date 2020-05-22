import csv
from pathlib import Path
from typing import Dict

cur_dir = Path(__file__).parent
PATH_DATA = cur_dir / 'data/type_effectiveness.csv'


class DefenseType:
    # TODO: Maybe just a PokeType class
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name.__eq__(other.name)


class AttackType:
    # TODO: Maybe just a PokeType class
    def __init__(self,
                 name: str,
                 effectiveness: Dict['DefenseType', int],
                 ):
        # TODO: load this in from csv
        self.name = name
        self.effectiveness = effectiveness

    def __repr__(self):
        return self.name

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name.__eq__(other.name)


attack_types = {}

with open(PATH_DATA) as csvfile:
    reader = csv.DictReader(csvfile)
    defense_types = {n.upper(): DefenseType(n.upper())
                     for n in reader.fieldnames[1:]}
    for row in reader:
        attack_type_name = row.pop('attack_type').upper()
        effectiveness = {
            defense_types.get(k.upper()): int(v)
            for k, v in row.items() if int(v)}
        attack_types[attack_type_name] = AttackType(
            attack_type_name.upper(), effectiveness)
