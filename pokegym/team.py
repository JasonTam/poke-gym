from pokegym.mon import Monster
from typing import List


class Team:
    def __init__(self):

        self.monsters: List[Monster]

        # In-battle Attributes
        self.n_shields: int = 2
