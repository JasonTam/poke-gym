import math
from dataclasses import dataclass
from typing import Set, Dict, Optional, TYPE_CHECKING

from pokegym.gamemaster import moves_raw_d
from pokegym.constants import STAB_MULT, EFFECTIVE_BASE
if TYPE_CHECKING:
    from pokegym.mon import Monster
from pokegym.poketypes import AttackType, attack_types


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class BuffChance:
    def __init__(self):

        self.target = 0  # Self or Enemy
        self.chance: float

        self.stat = None  # atk or def
        self.effect: int  # -2, -1, +1, +2

    # TODO:
    pass


def get_effectiveness(type_atk, types_def):
    return EFFECTIVE_BASE ** sum(
        type_atk.effectiveness.get(type_def, 0)
        for type_def in types_def)


@dataclass
class Move:
    name: str
    type_atk: AttackType
    power: int
    energy: int
    duration: int
    buff_chances: Optional[Set[BuffChance]]

    def __post_init__(self):
        pass

    @classmethod
    def from_dict(cls, template: Dict):
        move_info = template['combatMove']
        type_atk_str = move_info['type'].rsplit('_', 1)[-1]
        # template['templateId'].endswith('_FAST') else "charged"
        # if "buffs" in move_info:
        #     buffs = {
        #         "activation_chance": move_info["buffs"]["buffActivationChance"],
        #         "self_attack_stage_delta": move_info["buffs"].get(
        #             "attackerAttackStatStageChange", 0),
        #         "self_defense_stage_delta": move_info["buffs"].get(
        #             "attackerDefenseStatStageChange", 0),
        #         "target_attack_stage_delta": move_info["buffs"].get(
        #             "targetAttackStatStageChange", 0),
        #         "target_defense_stage_delta": move_info["buffs"].get(
        #             "targetDefenseStatStageChange", 0)
        #     }

        return cls(
            name=move_info['uniqueId'].upper(),
            type_atk=attack_types[type_atk_str.upper()],
            power=move_info.get('power', 0),
            energy=move_info.get('energyDelta', 0),
            duration=move_info.get('durationTurns', -1),
            buff_chances=None,  # TODO
        )

    def get_dmg(self, attacker: 'Monster', defender: 'Monster'):
        """
        https://gamepress.gg/pokemongo/damage-mechanics
        """
        # STAB [Same Type Attack Bonus]
        stab = (
            STAB_MULT if self.type_atk in attacker.species.types
            else 1.0
        )

        # TODO: need to define effectiveness structure somewhere
        effectiveness = get_effectiveness(
            self.type_atk, defender.species.types)

        dmg = math.floor(
            0.5
            * self.power
            * attacker.atk_tot / defender.def_tot
            * stab
            * effectiveness
        ) + 1
        return dmg


class FastMove(Move):
    # TODO: ?
    pass


class ChargeMove(Move):
    # TODO: ?
    pass


MOVES = AttrDict()
for k, v in moves_raw_d.items():
    MOVES[k] = Move.from_dict(v)
