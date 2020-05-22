from typing import List, Optional
from pokegym.mon import Monster
from pokegym.player import Player
from pokegym.gamemaster import combat_settings_d


DURATION_ROUND_SEC = combat_settings_d['roundDurationSeconds']
DURATION_TURN_SEC = combat_settings_d['turnDurationSeconds']
DURATION_MINIGAME_SEC = combat_settings_d['minigameDurationSeconds']


class Battle:

    def __init__(self, players=List[Player]):

        self.players = players

        self.timer: int = DURATION_ROUND_SEC
        self.turn = 0
        self.state: str  # TODO: this would be... enum/class?

    def battle(self):
        while all(p.is_alive for p in self.players) and (self.timer > 0):
            # Turn

            # Both players queue their actions

            # Resolve actions

            self.timer -= DURATION_TURN_SEC
            pass

        # Resolve winner
        winner = self.get_winner()

    def get_winner(self) -> Optional[Player]:
        n_alive = sum(p.is_alive for p in self.players)
        if n_alive == 1:
            # Clear winner
            return [p for p in self.players if p.is_alive][0]
        elif n_alive == 0:
            # Simultaneous KO -- No winner
            return None
        elif len(set(p.n_mons_alive for p in self.players)) > 1:
            # Tie-breaker: Balls remaining
            ind = self.players[0].n_mons_alive < self.players[1].n_mons_alive
            return self.players[ind]
        else:
            # Tie-breaker: HP remaining
            hp_tots = [sum(m.hp_cur for m in p.mons) for p in self.players]
            ind = hp_tots[0] < hp_tots[1]
            return self.players[ind]




