
# TODO


- [ ] Write test for dueling env
    - Test charge move logic more in-depth 
        (seems like there is sometimes 1 step of battle between cmp ties)
- [ ] Implement timer
- [ ] Handle Charge amount
- [ ] (De)Buffs
- [ ] Handle faints
    - do queued fast moves get removed?
- [ ] Hard coded policy
- [ ] Map / implement player actions
- [ ] Player observations of the visible game state
- [ ] Visual lag parameters (human doesnt instantaneously observe)
    - time to determine which fast move is being used
    - time to determine what swap came out
- [ ] Figure out exact swap mechanics
    - Do the opponents (fast/charge) moves apply to 
    the mon you previously had out, or the one you swapped to?
- [ ] 1 Agent to choose team, another agent to play the match
 
 
Observations:
- One-hot states
- Number of shields (both players)
- Known mons (moves when used)
- Mons left
- Time left
- Switch clocks (both players)
- Flag -- waiting for fast turn to finish
