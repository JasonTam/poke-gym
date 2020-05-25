import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding

from pokegym.player import Player
from pokegym.mon import Monster, POKEMON
from pokegym.move import MOVES
from pokegym.battle import Battle


def make_registeel():
    registeel = Monster(
        species=POKEMON.REGISTEEL,
        level=22.5,
        atk_iv=8,
        def_iv=15,
        stm_iv=13,
        move_fast=MOVES.LOCK_ON_FAST,
        move_charge_1=MOVES.FLASH_CANNON,
        move_charge_2=MOVES.FOCUS_BLAST,
    )
    return registeel


def make_chansey():
    chansey = Monster(
        species=POKEMON.CHANSEY,
        level=40,
        atk_iv=15,
        def_iv=15,
        stm_iv=15,
        move_fast=MOVES.POUND_FAST,
        move_charge_1=MOVES.PSYCHIC,
        move_charge_2=None,
    )
    return chansey


class EasyEnv(gym.Env):
    """
    Simple Env with set teams, and limited actions
    The goal of this env is to just keep attacking

    Simplified Actions:
    0: Fast Attack
    1: Charge Move 1
    2: Charge Move 2
    3: Do Nothing
    """
    metadata = {'render.modes': ['console']}

    def __init__(self):

        self.player_0 = Player(mons=[make_registeel()])
        self.player_1 = Player(mons=[make_chansey()])
        self.battle = Battle(players=[self.player_0, self.player_1])
        self.action_space = spaces.Discrete(4)

        # From perspective of player_0
        # Partially observed space of what player_1 has shown to us already

        # HACK: (B/C baseline models don't support Dict/Tuple)
        # Enemy HP, Energy -- both unit normalized
        self.observation_space = spaces.Box(
            low=np.array([0., 0.]),
            high=np.array([1., 1.]),
            dtype=np.float32,
        )

    def step(self, action):

        if action == 0:
            self.player_0.apply_fast_move(self.battle)
        elif action == 1:
            self.player_0.apply_charge_move_1(self.battle)
        elif action == 2:
            self.player_0.apply_charge_move_2(self.battle)
        elif action == 3:
            self.player_0.apply_wait(self.battle)

        o_hp_0 = self.player_1.mon_cur.hp_cur
        p_nrg_0 = self.player_0.mon_cur.energy
        self.battle.resolve_actions()
        o_hp_1 = self.player_1.mon_cur.hp_cur
        p_nrg_1 = self.player_0.mon_cur.energy

        observation = np.array([
            self.player_1.mon_cur.hp_cur / self.player_1.mon_cur.stm_tot,
            self.player_0.mon_cur.energy / 100.,
        ], dtype=np.float16)

        done = self.battle.is_done

        # Rewards
        r_dmg = 10 * ((o_hp_0 - o_hp_1) / self.player_1.mon_cur.stm_tot)
        r_nrg = 1 * ((p_nrg_1 - p_nrg_0) / 100.)
        # Promised energy (?)
        # Realized energy
        if self.battle.is_done:
            if self.battle.get_winner() == self.player_0:
                reward = 10 * (270 - self.battle.turn * 0.5)
            else:
                reward = 0
        else:
            reward = r_dmg + r_nrg

        # Optionally we can pass additional info, we are not using that for now
        info = {}

        return observation, reward, done, info

    def reset(self):
        self.battle.reset()

        observation = np.array([
            self.player_1.mon_cur.hp_cur / self.player_1.mon_cur.stm_tot,
            self.player_0.mon_cur.energy / 100.,
        ], dtype=np.float16)

        return observation

    def render(self, mode='console'):
        print(f'{self.player_1.mon_cur.hp_cur}/'
              f'{self.player_1.mon_cur.stm_tot}')

    def close(self):
        # Clean-up
        pass


if __name__ == '__main__':
    from stable_baselines.common.env_checker import check_env
    from stable_baselines import DQN, PPO2, A2C, ACKTR

    env = EasyEnv()

    check_env(env, warn=True)

    # Train the agent
    model = ACKTR('MlpPolicy', env, verbose=1).learn(10_000)

    # Test the trained agent
    obs = env.reset()
    n_steps = 300
    action_history = []
    for step in range(n_steps):
        action, _ = model.predict(obs, deterministic=True)
        action_history.append(action)
        print("Step {}".format(step + 1))
        print("Action: ", action)
        obs, reward, done, info = env.step(action)
        print('obs=', obs, 'reward=', reward, 'done=', done)
        env.render(mode='console')
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break

    print('*' * 40)
    print('Action History')
    print(action_history)

