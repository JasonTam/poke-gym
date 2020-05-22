from typing import List

from pokegym.mon import Monster
from pokegym.gamemaster import combat_settings_d


DURATION_SWAP_CD_SEC = combat_settings_d['quickSwapCooldownDurationSeconds']


class Player:

    def __init__(self, mons: List[Monster]):

        self.mons = mons
        self.n_shields = 2
        self.swap_cd = 0
        self.current_mon: Monster = self.mons[0]

    def swap(self, ind: int):
        if self.mons[ind].hp_cur > 0:
            self.current_mon = self.mons[ind]

        self.swap_cd = DURATION_SWAP_CD_SEC

    @property
    def is_alive(self) -> bool:
        return any(mon.is_alive for mon in self.mons)

    @property
    def n_mons_alive(self) -> int:
        return sum(mon.is_alive for mon in self.mons)

