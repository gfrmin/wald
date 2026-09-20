# Wordle — scoreboard

`packs/wordle/pack.py`, played by `wald.episode.run` through a door that answers with the
game's feedback. Every act is the kernel's own: the depth below is what the pack declares,
and the kernel plays `decide_min(d, n)` (CHARTER E3).

| | |
|---|---|
| words (states) | 40 |
| horizon | 5 (five guesses and a claim: Wordle's six attempts) |
| **declared depth** | **1** |
| answers played | 40 |
| solved | 40 / 40 |
| mean attempts | 2.250 |
| worst | 3 |
| time | 89.2 s for 40 episodes (2.23 s each) |

## Attempts

An attempt is an act the agent played: each guess, and the claim it ends on.

| attempts | answers | |
|---|---|---|
| 1 | 1 | # |
| 2 | 28 | ############################ |
| 3 | 11 | ########### |

## Failures

None: every answer was claimed right, or guessed all-green, within the horizon.

## Quantities by source

`wald.surface.census`, which counts quantities, not numerals: each cell, parameter,
mixture weight, price, the horizon and the depth once, however it is written.

| source | quantities |
|---|---|
| data | 1681 |
| elicited | 3202 |
| fitted | 0 |
| **total** | **4883** |

`fitted` is 0: nothing in this World is a point estimate. The prior, the prices, the
horizon and every kernel row are `data` — facts of the game and of the word list. What is
`elicited` is the owner's: the depth, and the utilities, including `loss`.

## Every answer

| answer | attempts | acts |
|---|---|---|
| about | 2 | their → claim about |
| other | 2 | their → claim other |
| which | 2 | their → claim which |
| their | 1 | their |
| there | 2 | their → claim there |
| first | 2 | their → claim first |
| would | 2 | their → would |
| these | 2 | their → claim these |
| click | 2 | their → click |
| price | 2 | their → claim price |
| state | 2 | their → claim state |
| email | 2 | their → claim email |
| world | 2 | their → world |
| music | 2 | their → claim music |
| after | 2 | their → claim after |
| video | 2 | their → video |
| where | 2 | their → claim where |
| books | 3 | their → would → claim books |
| links | 3 | their → click → claim links |
| years | 2 | their → claim years |
| order | 2 | their → order |
| items | 2 | their → claim items |
| group | 3 | their → world → claim group |
| under | 3 | their → order → claim under |
| games | 2 | their → games |
| could | 3 | their → would → claim could |
| great | 2 | their → claim great |
| hotel | 2 | their → claim hotel |
| store | 2 | their → claim store |
| terms | 2 | their → claim terms |
| right | 2 | their → claim right |
| local | 3 | their → would → claim local |
| those | 2 | their → claim those |
| using | 3 | their → click → claim using |
| phone | 2 | their → claim phone |
| forum | 3 | their → world → claim forum |
| based | 3 | their → games → claim based |
| black | 3 | their → would → claim black |
| check | 2 | their → claim check |
| index | 3 | their → video → claim index |
