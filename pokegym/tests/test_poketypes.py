

from pokegym.mon import POKEMON, Monster, MonsterSpecies, PURITY
from pokegym.poketypes import attack_types, defense_types
from pokegym.move import MOVES, Move, get_effectiveness


def test_3stage_ineffective_gm():
    stunfisk = POKEMON.STUNFISK
    my_stunfisk = Monster(
        species=stunfisk,
        level=1,
        atk_iv=0,
        def_iv=0,
        stm_iv=0,
        move_fast=None,
        move_charge_1=None,
        move_charge_2=None,
    )

    move = MOVES.THUNDER

    e = get_effectiveness(move.type_atk, my_stunfisk.species.types)

    assert (e - 0.24) < 0.01


def test_3stage_ineffective_hardcode():
    stunfisk = MonsterSpecies(
        name='STUNFISK',
        number=618,
        unique_id='V618_STUNFISK',
        purity=PURITY.NORMAL,
        atk_base=144,
        def_base=171,
        stm_base=240,
        type1=defense_types['GROUND'],
        type2=defense_types['ELECTRIC'],
        fast_moves=set(),
        charge_moves=set(),
    )

    my_stunfisk = Monster(
        species=stunfisk,
        level=1,
        atk_iv=0,
        def_iv=0,
        stm_iv=0,
        move_fast=None,
        move_charge_1=None,
        move_charge_2=None,
    )

    move = Move(
        name='THUNDER',
        type_atk=attack_types['ELECTRIC'],
        power=100,
        energy=60,
        duration=None,
        buff_chances=set(),
    )

    e = get_effectiveness(move.type_atk, my_stunfisk.species.types)

    assert (e - 0.24) < 0.01

