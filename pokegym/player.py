from typing import List, TYPE_CHECKING

from pokegym.mon import Monster
from pokegym.gamemaster import combat_settings_d
if TYPE_CHECKING:
    from pokegym.battle import Battle

DURATION_SWAP_CD_SEC = combat_settings_d['quickSwapCooldownDurationSeconds']


class Player:

    def __init__(self, mons: List[Monster]):

        self.mons = mons
        self.n_shields = 2
        self.swap_cd = 0
        self.mon_cur: Monster = self.mons[0]

    def swap(self, ind: int):
        if self.mons[ind].hp_cur > 0:
            self.mon_cur = self.mons[ind]

        self.swap_cd = DURATION_SWAP_CD_SEC

    @property
    def is_alive(self) -> bool:
        return any(mon.is_alive for mon in self.mons)

    @property
    def n_mons_alive(self) -> int:
        return sum(mon.is_alive for mon in self.mons)

    # Actions that a player can take in a battle environment
    def apply_fast_move(self, b: 'Battle'):
        b.store_action(self, self.mon_cur.move_fast, 1)

    def apply_charge_move_1(self, b: 'Battle'):
        b.store_action(self, self.mon_cur.move_charge_1, 2)

    def apply_charge_move_2(self, b: 'Battle'):
        b.store_action(self, self.mon_cur.move_charge_2, 2)

    # TODO: should these be.... lambdas??
    def apply_swap_mon_1(self, b: 'Battle'):
        def lazy_swap():
            tmp = self.mons[0]
            self.mons[0] = self.mon_cur
            self.mon_cur = tmp
        b.store_action(self, lazy_swap, 0)

    def apply_swap_mon_2(self, b: 'Battle'):
        def lazy_swap():
            tmp = self.mons[1]
            self.mons[1] = self.mon_cur
            self.mon_cur = tmp
        b.store_action(self, lazy_swap, 0)

    def apply_wait(self, b: 'Battle'):
        b.store_action(self, lambda: None, 0)

