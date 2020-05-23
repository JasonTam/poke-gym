from dataclasses import dataclass
from typing import List, Optional
from pokegym.mon import Monster
from pokegym.player import Player
from pokegym.move import FastMove
from pokegym.gamemaster import combat_settings_d
from typing import Any


DURATION_ROUND_SEC = combat_settings_d['roundDurationSeconds']
DURATION_TURN_SEC = combat_settings_d['turnDurationSeconds']
DURATION_MINIGAME_SEC = combat_settings_d['minigameDurationSeconds']


@dataclass
class QAction:
    player: Player
    action: Any  # TODO: Could be more specific
    priority: int
    turns_elapsed: int = 0


class Battle:

    def __init__(self, players=List[Player]):

        self.players = players

        self.timer: int = DURATION_ROUND_SEC
        self.turn = 0
        self.state: str  # TODO: this would be... enum/class?
        self.stored_actions: List[QAction] = []
        self.attack_queue: List[QAction] = []

    def store_action(self, p: Player, action, priority: int):
        ind = self.players.index(p)

        self.stored_actions.append(QAction(p, action, priority, 0))

    def resolve_actions(self):
        """Logic for resolving actions in correct order
        Priority:
        - 0: Swap & no-ops & middle of fast move
        - 1: Fast Move
        - 2: Charge Move

        Actions at each priority stage have their own tie-breaking logic (2)
        otherwise, they are order independent within the same stage (0, 1)
        """

        # TODO: this is messy AF
        # TODO: actually, the fast move is kind of complicated
        #   need to queue the damage.....
        #   The current implementation here is not correct
        for i in range(3):
            cur_p_actions = [a for a in self.stored_actions
                             if a.priority == i]
            self.stored_actions = [a for a in self.stored_actions
                                   if a.priority != i]
            if i == 0:
                for a in cur_p_actions:
                    a.action()
            elif i == 1:
                for a in cur_p_actions:
                    if isinstance(a.action, FastMove):
                        self.attack_queue.append(a)
            elif i == 2:
                if len(cur_p_actions) > 1:
                    # Resolve CMP ties for charge moves
                    atk_stats = [p.current_mon.atk_tot for p in self.players]
                    for _, a in sorted(zip(atk_stats, cur_p_actions)):
                        # TODO: lol... is this even remotely correct??
                        self.attack_queue.append(a)

        for qa in self.attack_queue:
            qa.turns_elapsed += 1
        self.resolve_attacks()
        # TODO: lower the turns on all the queued attacks now
        self.turn += 1

    def get_other_player(self, player: Player) -> Player:
        return self.players[not self.players.index(player)]

    def resolve_attacks(self):
        ready_actions = [qa for qa in self.attack_queue
                         if qa.turns_elapsed >= qa.action.turns]
        self.attack_queue = [qa for qa in self.attack_queue
                             if qa.turns_elapsed < qa.action.turns]

        for qa in ready_actions:
            attacker = qa.player.mon_cur
            defender = self.get_other_player(qa.player).mon_cur
            move = qa.action
            # Apply Damage
            dmg = move.get_dmg(attacker, defender)
            defender.hp_cur -= dmg
            # Reward Energy
            attacker.energy += move.energy

    @property
    def is_done(self):
        return not (all(p.is_alive for p in self.players) and (self.timer > 0))

    def post_turn(self):
        # Resolve actions
        self.turn += 1
        self.timer -= DURATION_TURN_SEC

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




