from pokegym.player import Player
from pokegym.mon import Monster, POKEMON
from pokegym.move import MOVES
from pokegym.battle import Battle


def test_fast_move_duration():
    hypno = Monster(
        species=POKEMON.HYPNO,
        level=1,
        atk_iv=0,
        def_iv=0,
        stm_iv=0,
        move_fast=MOVES.CONFUSION_FAST,
        move_charge_1=MOVES.SHADOW_BALL,
        move_charge_2=None,
    )

    registeel = Monster(
        species=POKEMON.REGISTEEL,
        level=1,
        atk_iv=0,
        def_iv=0,
        stm_iv=0,
        move_fast=MOVES.LOCK_ON_FAST,
        move_charge_1=MOVES.FOCUS_BLAST,
        move_charge_2=None,
    )

    p0 = Player(mons=[hypno])
    p1 = Player(mons=[registeel])
    hp_start_0 = p0.mon_cur.hp_cur
    hp_start_1 = p1.mon_cur.hp_cur
    b = Battle(players=[p0, p1])

    # Turn 1
    p0.apply_fast_move(b)
    p1.apply_fast_move(b)
    assert p0.mon_cur.hp_cur == hp_start_0
    assert p1.mon_cur.hp_cur == hp_start_1
    b.resolve_actions()
    assert p0.mon_cur.hp_cur == hp_start_0 - 1
    assert p1.mon_cur.hp_cur == hp_start_1 - 0
    assert p0.mon_cur.energy == 0
    assert p1.mon_cur.energy == 5

    # Turn 2
    p0.apply_wait(b)
    p1.apply_fast_move(b)
    b.resolve_actions()
    assert p0.mon_cur.hp_cur == hp_start_0 - 2
    assert p1.mon_cur.hp_cur == hp_start_1 - 0
    assert p0.mon_cur.energy == 0
    assert p1.mon_cur.energy == 10

    # Turn 3
    p0.apply_wait(b)
    p1.apply_fast_move(b)
    b.resolve_actions()
    assert p0.mon_cur.hp_cur == hp_start_0 - 3
    assert p1.mon_cur.hp_cur == hp_start_1 - 0
    assert p0.mon_cur.energy == 0
    assert p1.mon_cur.energy == 15

    # Turn 4
    p0.apply_wait(b)
    p1.apply_fast_move(b)
    b.resolve_actions()
    assert p0.mon_cur.hp_cur == hp_start_0 - 4
    assert p1.mon_cur.hp_cur == hp_start_1 - 4
    assert p0.mon_cur.energy == 12
    assert p1.mon_cur.energy == 20

    # Turn 5
    p0.apply_fast_move(b)
    p1.apply_fast_move(b)
    b.resolve_actions()
    assert p0.mon_cur.hp_cur == hp_start_0 - 5
    assert p1.mon_cur.hp_cur == hp_start_1 - 4
    assert p0.mon_cur.energy == 12
    assert p1.mon_cur.energy == 25


if __name__ == '__main__':
    test_fast_move_duration()
