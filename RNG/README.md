
# Randomness in Rugrats: Search for Reptar

## RNG Implementation
RSfR uses a modified linear congruential generator or [LCG](https://en.wikipedia.org/wiki/Linear_congruential_generator), the specifics of which can be found in the **LCG Specifics** section of the appendix. Interestingly, it appears the seed for the LCG is statically defined and initialized at boot. This is likely due to the fact the PS1 does not have an internal clock (or other easy source of entropy). Practically, this means as long as a speedrunner is able to accurately reproduce their inputs, the game will behavior the same way every time.

## Manipulation
As the community has already observed and as mentioned above, it is possible to manipulate key RNG elements of the game.  By observing or performing specific actions in the game the current RNG value can be controlled. An example of this is the `Chuckie's Glasses` manipulation which uses actions that happen on the main screen to precisely increment the RNG. By subsequently controlling the number of steps Tommy takes before starting the level an ideal location of NPCs can be achieved.

While this type of manipulation is possible early game, the longer a run goes on the more likely a runner is to deviate from a pre-planned route. With no (currently) known way to reset the LCG, this means any RNG manipulations desired should occur at the beginning of the route. Additionally, actions that result in a call to the main RNG function should be cataloged. To this end, an incomplete list of actions that increment RNG has been provided in the appendix.

## Research Tools and Future Work
As part of this and to enable future work, two small tools have been create. This first is a lua script `rng_display.lua` which can be used with Bizhawk (or similar) to display the current RNG value. Additionally, the number of times the RNG value has changed _between consecutive frames_ is tracked. Importantly, this number does **not** accurately reflect the number of times the RNG value has been incremented. It provides a rough approximation and is mainly included as a simple way to verify the RNG value has changed. This script is intended to be used for dynamic analysis and RNG manipulation training.

For more precise RNG prediction and improved static analysis the Python file `RugratsRand.py` has been created. The `RugratsRand` class reimplements the LCG as seen in RSfR. While the file is intended as a foundation for future work, it can also be called as a standalone script that will generate the next `N` random numbers given a starting seed. By default, the boot seed is used.


## Appendix

### LCG Specifics
 - Seed on Boot: `0x02DCF1A5`
 - Multiplier: `0x000343FD`
- Increment: `0x00269EC3`
- Modulus `2^32` (32 bits)
- Function implemented at: `0x8002fb7c`
- The output of the main (only?) LCG is reduced to a single byte using the following method:
	- `newestRandomNumber >> 0x10 & 0xff`

### Actions Known to (Not) Increment RNG [Exceedingly Incomplete]
| Action | Resulting RNG Calls| Notes|
| --- | ----------- | ---- |
| Main Menu| ~4 per baby popping out | appears to come in sets of 2|
| Starting Main Game | 9 | 7 before the cutsceen, 1 from cutsceen to puzzle piece, 1 from puzzle piece menu to spawn |
| Walking | 1 per full step| Likely related to selecting the sound clip to play. Can be avoided by rapidly pressing the walk button. It looks like a one-legged-wobble |
| Jumping | 0 | Another good movement option if you don't want to increment RNG |
| Playing Piano | 1 |
