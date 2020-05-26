import numpy as np
import pandas as pd
import gym
from gym import error, spaces, utils
from gym.utils import seeding

from pokegym.player import Player
from pokegym.mon import Monster, POKEMON
from pokegym.move import MOVES
from pokegym.battle import Battle, BattleState, CHARGE_STATES


def make_registeel():
    registeel = Monster(
        species=POKEMON.REGISTEEL,
        level=22.5,
        atk_iv=8,
        def_iv=15,
        stm_iv=13,
        move_fast=MOVES.LOCK_ON_FAST,
        # move_fast=MOVES.METAL_CLAW_FAST,
        # move_charge_1=MOVES.FLASH_CANNON,
        move_charge_1=MOVES.CROSS_POISON,
        move_charge_2=MOVES.FOCUS_BLAST,
    )
    return registeel


class DuelingEnv(gym.Env):
    """

    Actions:
    0: Fast Attack
    1: Charge Move 1
    2: Charge Move 2
    3: Do Nothing
    4: Use Shield
    """
    metadata = {'render.modes': ['console']}

    def __init__(self, p1_agent):

        self.p1_agent = p1_agent
        self.p1_action: int

        self.player_0 = Player(mons=[make_registeel()])
        self.player_1 = Player(mons=[make_registeel()])
        self.battle = Battle(players=[self.player_0, self.player_1])
        self.action_space = spaces.Discrete(5)

        # From perspective of player_0
        # Partially observed space of what player_1 has shown to us already

        # HACK: (B/C baseline models don't support Dict/Tuple)
        # Enemy HP, Energy -- both unit normalized
        self.observation_space = spaces.Box(
            low=np.array([0.] * 9),
            high=np.array([1.] * 9),
            dtype=np.float32,
        )

    def _observations_common(self):
        """Observations known to both players
        NOTE: Needs to be flattened later
        Kept as 2 dimensional to easily flip perspective
        with np.flip(..., axis=1)
        """
        ps = self.battle.players
        mons = [p.mon_cur for p in ps]
        hp_rats = [mon.hp_cur / mon.stm_tot for mon in mons]
        nrg = [mon.energy / 100. for mon in mons]

        charge_state_ohe = [self.battle.state == s for s in CHARGE_STATES]
        n_shields = [p.n_shields / 2. for p in ps]

        obs_perspective = np.array([
            hp_rats,
            nrg,
            n_shields,
            charge_state_ohe,
        ], dtype=np.float16)

        obs_global = np.array([
            self.battle.state == BattleState.BATTLE,
        ])

        return obs_perspective, obs_global

    def _observations(self):
        com_persp_obs, com_global_obs = self._observations_common()
        p0_obs = np.concatenate([
            com_persp_obs.flatten(),
            com_global_obs,
        ], axis=0)
        p1_obs = np.concatenate([
            np.flip(com_persp_obs, axis=1).flatten(),
            com_global_obs,
        ], axis=0)

        return p0_obs, p1_obs

    def step(self, p0_action):

        for p, action in zip([self.player_0, self.player_1],
                             [p0_action, self.p1_action]):
            if action == 0:
                p.apply_fast_move(self.battle)
            elif action == 1:
                p.apply_charge_move_1(self.battle)
            elif action == 2:
                p.apply_charge_move_2(self.battle)
            elif action == 3:
                p.apply_wait(self.battle)
            elif action == 4:
                p.apply_shield()

        o_hp_0 = self.player_1.mon_cur.hp_cur
        p_nrg_0 = self.player_0.mon_cur.energy
        self.battle.resolve_actions()
        o_hp_1 = self.player_1.mon_cur.hp_cur
        p_nrg_1 = self.player_0.mon_cur.energy

        p0_obs, p1_obs = self._observations()

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

        # This is our opponent's move for next turn
        self.p1_action, _ = self.p1_agent.predict(p1_obs)

        return p0_obs, reward, done, info

    def reset(self):
        self.battle.reset()

        p0_obs, p1_obs = self._observations()

        # This is our opponent's move for next turn
        self.p1_action, _ = self.p1_agent.predict(p1_obs)

        return p0_obs

    def render(self, mode='console'):
        p0_mon = self.player_0.mon_cur
        p1_mon = self.player_1.mon_cur
        p0_hp = f'HP: {p0_mon.hp_cur}/' \
                f'{p0_mon.stm_tot}'
        p0_nrg = f'E: {p0_mon.energy}'
        p1_hp = f'HP: {p1_mon.hp_cur}/' \
                f'{p1_mon.stm_tot}'
        p1_nrg = f'E: {p1_mon.energy}'

        print(p0_hp, p1_hp, sep='\t')
        print(p0_nrg, p1_nrg, sep='\t')

    def close(self):
        # Clean-up
        pass


if __name__ == '__main__':
    from stable_baselines.common.env_checker import check_env
    from stable_baselines import DQN, PPO2, A2C, ACKTR
    from pathlib import Path

    PATH_SAVE = './saved/shit.p'

    class ShittyAgent:
        def predict(self, obs):
            return np.random.randint(5), None

    for epoch in range(10):
        print('*' * 60)
        print(f'EPOCH {epoch}')
        print('*' * 60)

        if Path(PATH_SAVE).exists():
            print('Loading saved model')
            opponent = ACKTR.load(PATH_SAVE)
        else:
            print('No model found, using random agent')
            opponent = ShittyAgent()

        env = DuelingEnv(opponent)

        check_env(env, warn=True)

        # Train the agent
        model = ACKTR('MlpPolicy', env, verbose=0).learn(20_000)

        # Test the trained agent
        obs = env.reset()
        n_steps = 300
        action_history = []
        for step in range(n_steps):
            action, _ = model.predict(obs, deterministic=True)
            action_history.append(action)
            print("Step {}".format(step + 1))
            print(f"P0_Action: {action} \t P1_Action: {env.p1_action}")
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

        print('Saving Model')
        model.save(PATH_SAVE)


