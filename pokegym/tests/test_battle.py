from pokegym.player import Player
from pokegym.mon import Monster, POKEMON
from pokegym.move import MOVES
from pokegym.battle import Battle


def make_dummy_mon():
    m = Monster(
        species=POKEMON.BULBASAUR,
        level=1,
        atk_iv=0,
        def_iv=0,
        stm_iv=0,
        move_fast=MOVES.TACKLE_FAST,
        move_charge_1=MOVES.POWER_WHIP,
        move_charge_2=None,
    )
    return m


def test_win_clear():
    p0 = Player(mons=[make_dummy_mon()] * 3)
    p1 = Player(mons=[make_dummy_mon()] * 3)
    b = Battle(players=[p0, p1])

    for mon in p0.mons:
        mon.hp_cur = 0

    assert b.get_winner() == p1


def test_simul_ko():
    p0 = Player(mons=[make_dummy_mon() for _ in range(3)])
    p1 = Player(mons=[make_dummy_mon() for _ in range(3)])
    b = Battle(players=[p0, p1])

    for mon in p0.mons:
        mon.hp_cur = 0
    for mon in p1.mons:
        mon.hp_cur = 0

    assert b.get_winner() is None


def test_tie_balls():
    p0 = Player(mons=[make_dummy_mon() for _ in range(3)])
    p1 = Player(mons=[make_dummy_mon() for _ in range(3)])
    b = Battle(players=[p0, p1])

    for mon in p0.mons:
        mon.hp_cur = 999
    for mon in p1.mons:
        mon.hp_cur = 1
    p0.mons[0].hp_cur = 0

    assert b.get_winner() == p1


def test_tie_hp():
    p0 = Player(mons=[make_dummy_mon() for _ in range(3)])
    p1 = Player(mons=[make_dummy_mon() for _ in range(3)])
    b = Battle(players=[p0, p1])

    for mon in p0.mons:
        mon.hp_cur = 1
    for mon in p1.mons:
        mon.hp_cur = 2
    p0.mons[0].hp_cur = 0
    p1.mons[0].hp_cur = 0

    assert p0.n_mons_alive == p1.n_mons_alive
    assert b.get_winner() == p1

