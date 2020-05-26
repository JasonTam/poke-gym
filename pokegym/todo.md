
# TODO

- [ ] Fix tiebreaker to be HP percentage -- not total HP
- [ ] Extend basic env to 2 competing agents
- [ ] Implement shield state & logic
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
 
 
Observations:
- One-hot states
- Number of shields (both players)
- Known mons (moves when used)
- Mons left
- Time left
- Switch clocks (both players)
- Flag -- waiting for fast turn to finish
