from enum import Enum
from dataclasses import dataclass
from typing import Set, Optional, Dict, List

from pokegym.gamemaster import pokemon_raw_d, level_to_cpm, combat_settings_d
from pokegym.poketypes import DefenseType, defense_types
from pokegym.move import FastMove, ChargeMove


MAX_ENERGY = combat_settings_d['maxEnergy']


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class PURITY(Enum):
    NORMAL = 'NORMAL'
    SHADOW = 'SHADOW'
    PURIFIED = 'PURIFIED'


@dataclass
class MonsterSpecies:
    unique_id: str
    name: str
    number: int
    purity: PURITY
    atk_base: int
    def_base: int
    stm_base: int
    type1: DefenseType
    type2: DefenseType
    fast_moves: Set[FastMove]
    charge_moves: Set[ChargeMove]

    def __post_init__(self):
        pass

    @property
    def types(self):
        return {self.type1, self.type2}

    @classmethod
    def from_dict(cls, template: Dict):
        template_id = template['templateId']
        pkm_info = template["pokemon"]
        if template_id.split('_')[-1] in PURITY.__members__:
            purity = template_id.split('_')[-1]
        else:
            purity = None
        return cls(
            unique_id=template_id,
            name=pkm_info['uniqueId'],  # not actually unique
            number=int(template_id.split('_')[0][1:]),
            purity=purity,
            type1=defense_types.get(pkm_info['type1'].split('_')[-1]),
            type2=defense_types.get(pkm_info.get('type2', '').split('_')[-1],
                                    None),
            atk_base=pkm_info['stats']['baseAttack'],
            def_base=pkm_info['stats']['baseDefense'],
            stm_base=pkm_info['stats']['baseStamina'],
            fast_moves=[m.rsplit('_', 1)[0]
                        for m in pkm_info.get('quickMoves', [])],
            charge_moves=pkm_info.get('cinematicMoves', []),
        )


POKEMON = AttrDict()
for k, v in pokemon_raw_d.items():
    POKEMON[k] = MonsterSpecies.from_dict(v)


@dataclass
class Monster:
    species: MonsterSpecies
    level: float
    atk_iv: int  # assert in range(0, 15+1)
    def_iv: int  # assert in range(0, 15+1)
    stm_iv: int  # assert in range(0, 15+1)
    move_fast: FastMove
    move_charge_1: ChargeMove
    move_charge_2: Optional[ChargeMove]

    def __post_init__(self):
        # In-battle Attributes
        self.energy = 0  # assert in range(100+1)
        self.debuffs = []
        self.hp_cur: int = self.stm_tot

    @property
    def cpm(self) -> float:
        return level_to_cpm[self.level]

    @property
    def atk_tot(self) -> float:
        return (self.species.atk_base + self.atk_iv) * self.cpm

    @property
    def def_tot(self) -> float:
        return (self.species.def_base + self.def_iv) * self.cpm

    @property
    def stm_tot(self) -> int:
        return int((self.species.stm_base + self.stm_iv) * self.cpm)

    @property
    def cp(self) -> int:
        return max(
            10, int(self.atk_tot * (self.def_tot * self.stm_tot)**0.5 / 10))

    @property
    def is_alive(self) -> bool:
        return self.hp_cur > 0

    def attack_fast(self, other: 'Monster'):
        # NOTE: these actions are meant to be put into a queue
        dmg = self.move_fast.get_dmg(self, other)
        other.hp_cur -= dmg
        self.energy = min(self.energy + self.move_fast.energy, MAX_ENERGY)

    def attack_charge(self, move: ChargeMove, other: 'Monster'):
        # NOTE: these actions are meant to be put into a queue
        # and CMP ties must be resolved
        if self.energy >= move.energy:
            dmg = move.get_dmg(self, other)
            other.hp_cur -= dmg
            # NOTE: charge move energies are negative
            self.energy = self.energy + move.energy

    def attack_charge_1(self, other: 'Monster'):
        return self.attack_charge(self.move_charge_1, other)

    def attack_charge_2(self, other: 'Monster'):
        return self.attack_charge(self.move_charge_2, other)


