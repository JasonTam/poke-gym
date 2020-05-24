"""
The action space of various states:

Battle State:
- Fast Move
- Energy Permitting:
    - Charge Move1
    - Charge Move2
- Switch Timer Permitting & Monster(s) on Bench:
    - Switch
- Do nothing

Charge Move State:
- Number of bubbles to hit

Defending State:
- No Shield
- Shields Remaining:
    - Use shield

Fainted Forced Swap State:
(Requires 2 in the bench)
- Switch
- Wait
- Completely wait out and autochoose 1
"""

import gym
from gym import spaces

# TODO: Potentially apply a mask of valid actions


ACTIONS_BATTLE = {
    0: 'fast_move',
    1: 'charge_move_1',
    2: 'charge_move_2',
    3: 'swap_mon_1',
    4: 'swap_mon_2',
    5: 'wait',
}

ACTIONS_CHARGE = {
    0: 'base',
    1: 'nice',
    2: 'great',
    3: 'excellent',
}

ACTIONS_DEFEND = {
    0: 'no shield',
    1: 'use shield',
}

ACTIONS_FAINT_SWAP = {
    0: 'swap_mon_1',
    1: 'swap_mon_2',
    2: 'wait_swap_mon_1',
    3: 'wait_swap_mon_2',
    4: 'wait_rand',
}

actions_battle = spaces.Discrete(len(ACTIONS_BATTLE))
actions_charge = spaces.Discrete(len(ACTIONS_CHARGE))
actions_defend = spaces.Discrete(len(ACTIONS_DEFEND))
actions_faint_swap = spaces.Discrete(len(ACTIONS_FAINT_SWAP))


# TODO: Keys are actually states...
#     Might want to just concat and have the agent determine by its own
#     exploration strategy that those options are invalid?
#     Otherwise, have a way to mask them off or set probabilities to 0
nested_action_space = spaces.Dict({
    'battle': actions_battle,
    'charge': actions_charge,
    'defend': actions_defend,
    'faint_swap': actions_faint_swap,
})
