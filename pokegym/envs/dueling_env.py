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
        move_fast=MOVES.METAL_CLAW_FAST,
        move_charge_1=MOVES.FLASH_CANNON,
        move_charge_2=MOVES.FOCUS_BLAST,
    )
    return registeel


class DuelingEnv(gym.Env):
    """

    Simplified Actions:
    0: Fast Attack
    1: Charge Move 1
    2: Charge Move 2
    3: Do Nothing
    """
    metadata = {'render.modes': ['console']}

    def __init__(self, p1_agent):

        self.p1_agent = p1_agent
        self.p1_action: int

        self.player_0 = Player(mons=[make_registeel()])
        self.player_1 = Player(mons=[make_registeel()])
        self.battle = Battle(players=[self.player_0, self.player_1])
        self.action_space = spaces.Discrete(4)

        # From perspective of player_0
        # Partially observed space of what player_1 has shown to us already

        # HACK: (B/C baseline models don't support Dict/Tuple)
        # Enemy HP, Energy -- both unit normalized
        self.observation_space = spaces.Box(
            low=np.array([0., 0., 0., 0.]),
            high=np.array([1., 1., 1., 1.]),
            dtype=np.float32,
        )

    def _observations_common(self):
        """Observations known to both players
        NOTE: Needs to be flattened later
        Kept as 2 dimensional to easily flip perspective
        with np.flip(..., axis=1)
        """
        p0_mon = self.player_0.mon_cur
        p1_mon = self.player_1.mon_cur

        p0_hp_rat = p0_mon.hp_cur / p0_mon.stm_tot
        p1_hp_rat = p1_mon.hp_cur / p1_mon.stm_tot

        p0_nrg = p0_mon.energy / 100.
        p1_nrg = p1_mon.energy / 100.

        obs_perspective = np.array([
            [p0_hp_rat, p1_hp_rat],
            [p0_nrg, p1_nrg],
        ], dtype=np.float16)
        # TODO: charge move state needs to be here too ^

        obs_global = np.array([])

        return obs_perspective

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

        o_hp_0 = self.player_1.mon_cur.hp_cur
        p_nrg_0 = self.player_0.mon_cur.energy
        self.battle.resolve_actions()
        o_hp_1 = self.player_1.mon_cur.hp_cur
        p_nrg_1 = self.player_0.mon_cur.energy

        common_obs = self._observations_common()
        p0_obs = common_obs.flatten()
        p1_obs = np.flip(common_obs, axis=1).flatten()

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

        common_obs = self._observations_common()
        p0_obs = common_obs.flatten()
        p1_obs = np.flip(common_obs, axis=1).flatten()

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

    class ShittyAgent:
        def predict(self, obs):
            return np.random.randint(4), None

    # opponent = ShittyAgent()
    opponent = ACKTR.load('./saved/shit.p')

    env = DuelingEnv(opponent)

    check_env(env, warn=True)

    # Train the agent
    model = ACKTR('MlpPolicy', env, verbose=1).learn(50_000)

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

