# Wordle — scoreboard

`packs/wordle200/d1.py`, `packs/wordle200/d2.py`, `packs/wordle200/adaptive.py`, played by `wald.episode.run` through a door that answers
with the game's feedback. Every act is the kernel's own: the depth below is what the pack
declares, and the kernel plays `decide_min(d, n)` (CHARTER E3).

One of these packs declares a **think act** (CHARTER v0.1): at a step with room left it
may buy one deeper look, at a price the pack itself declares, and play the act that look
found. Its column says `1 + θ` — the floor is still 1, and what it buys is not a depth it
declares but a computation the one `decide` chose to pay for.

|  | **depth 1** | **depth 2** | **depth 1 + θ** |
|---|---|---|---|
| words (states) | 200 | 200 | 200 |
| horizon | 5 | 5 | 5 |
| **declared depth** | **1** | **2** | **1** + θ |
| answers played | 200 | 200 | 200 |
| solved | 200 / 200 | 200 / 200 | 200 / 200 |
| **mean attempts** | **2.645** | **2.645** | **2.645** |
| worst | 4 | 4 | 4 |
| first episode | 1.8 s | 32.3 s | 34.5 s |
| all answers | 2.1 s | 45.2 s | 63.1 s |

**The price of the floor, measured.** Mean attempts at depth 1 minus mean attempts at depth 2, over all 200 answers, is **0.000**. Nothing here is tuned to make it larger: the two packs differ in one line.

The two depths are not playing the same game, though. They play 8 of the 200 answers differently: `might`, `photo`, `think`, `point`, `topic`, `night`, `light`, `thing`. Of those, the
deeper agent needs fewer attempts on 1 and more on 1.

## Quantities by source

`wald.surface.census`, which counts quantities, not numerals: each cell, parameter,
mixture weight, price, the horizon and the depth once, however it is written.

| source | depth 1 | depth 2 | depth 1 + θ |
|---|---|---|---|
| data | 40401 | 40401 | 40402 |
| elicited | 80002 | 80002 | 80005 |
| fitted | 0 | 0 | 202 |
| **total** | **120403** | **120403** | **120609** |

The prior, the prices, the horizon and every kernel row are `data` — facts of the game
and of the word list. What is `elicited` is the owner's: the depth, the utilities,
including `loss`, and — where a think act is declared — Depth⁺, the Fraction and the
Rate. What is `fitted` is the Cost table: two parameters fitted by the author to the
kernel's own operation counts, read by 200 cells, each of which counts once under
its table's source (SURFACE v0.1 K17). A fitted table carries its held-out Score, and
this one does.

## Depth 1 — `packs/wordle200/d1.py`

An attempt is an act the agent played: each guess, and the claim it ends on.

| attempts | answers |  |
|---|---|---|
| 1 | 1 | # |
| 2 | 71 | ####################### |
| 3 | 126 | ######################################## |
| 4 | 2 | # |

Failures: none — every answer was claimed right, or guessed all-green, within the horizon.

<details><summary>every answer</summary>

| answer | attempts | acts |
|---|---|---|
| about | 2 | rates → claim about |
| other | 2 | rates → other |
| which | 3 | rates → would → claim which |
| their | 2 | rates → their |
| there | 3 | rates → their → claim there |
| first | 2 | rates → first |
| would | 2 | rates → would |
| these | 2 | rates → these |
| click | 3 | rates → would → claim click |
| price | 2 | rates → price |
| state | 2 | rates → state |
| email | 3 | rates → place → claim email |
| world | 2 | rates → world |
| music | 2 | rates → music |
| after | 2 | rates → claim after |
| video | 3 | rates → women → claim video |
| where | 3 | rates → price → claim where |
| books | 2 | rates → books |
| links | 3 | rates → books → claim links |
| years | 2 | rates → years |
| order | 3 | rates → would → claim order |
| items | 2 | rates → claim items |
| group | 3 | rates → world → claim group |
| under | 3 | rates → would → claim under |
| games | 2 | rates → games |
| could | 3 | rates → would → claim could |
| great | 2 | rates → great |
| hotel | 2 | rates → hotel |
| store | 2 | rates → claim store |
| terms | 2 | rates → claim terms |
| right | 2 | rates → claim right |
| local | 3 | rates → along → claim local |
| those | 3 | rates → these → claim those |
| using | 3 | rates → music → claim using |
| phone | 2 | rates → phone |
| forum | 3 | rates → world → claim forum |
| based | 2 | rates → claim based |
| black | 3 | rates → along → claim black |
| check | 3 | rates → phone → claim check |
| index | 3 | rates → women → claim index |
| might | 3 | rates → login → claim might |
| house | 2 | rates → house |
| women | 2 | rates → women |
| south | 3 | rates → would → claim south |
| pages | 3 | rates → games → claim pages |
| found | 3 | rates → would → claim found |
| photo | 3 | rates → login → claim photo |
| power | 3 | rates → would → claim power |
| while | 3 | rates → phone → claim while |
| three | 3 | rates → other → claim three |
| total | 2 | rates → claim total |
| place | 2 | rates → place |
| think | 3 | rates → login → claim think |
| north | 2 | rates → north |
| posts | 2 | rates → posts |
| media | 3 | rates → place → claim media |
| water | 2 | rates → water |
| since | 3 | rates → house → claim since |
| guide | 3 | rates → phone → claim guide |
| board | 2 | rates → board |
| white | 2 | rates → white |
| small | 2 | rates → small |
| times | 2 | rates → times |
| sites | 2 | rates → sites |
| level | 3 | rates → women → claim level |
| hours | 3 | rates → works → claim hours |
| image | 3 | rates → place → claim image |
| title | 2 | rates → claim title |
| shall | 3 | rates → small → claim shall |
| class | 2 | rates → class |
| still | 3 | rates → would → claim still |
| money | 3 | rates → women → claim money |
| every | 3 | rates → price → claim every |
| visit | 3 | rates → would → claim visit |
| tools | 3 | rates → posts → claim tools |
| reply | 2 | rates → claim reply |
| value | 2 | rates → value |
| press | 2 | rates → press |
| learn | 2 | rates → learn |
| print | 3 | rates → north → claim print |
| stock | 3 | rates → would → claim stock |
| point | 3 | rates → login → claim point |
| sales | 3 | rates → games → sales |
| large | 2 | rates → large |
| table | 2 | rates → claim table |
| start | 2 | rates → claim start |
| model | 3 | rates → women → claim model |
| human | 3 | rates → along → claim human |
| movie | 3 | rates → phone → claim movie |
| march | 2 | rates → march |
| going | 3 | rates → would → claim going |
| study | 3 | rates → would → claim study |
| staff | 2 | rates → claim staff |
| again | 3 | rates → along → claim again |
| never | 3 | rates → would → never |
| users | 3 | rates → press → claim users |
| topic | 3 | rates → login → claim topic |
| below | 3 | rates → phone → claim below |
| party | 2 | rates → claim party |
| login | 3 | rates → would → claim login |
| legal | 3 | rates → place → claim legal |
| above | 3 | rates → place → claim above |
| quote | 3 | rates → white → claim quote |
| story | 3 | rates → first → claim story |
| rates | 1 | rates |
| young | 3 | rates → would → claim young |
| field | 3 | rates → phone → claim field |
| paper | 2 | rates → claim paper |
| night | 3 | rates → login → claim night |
| issue | 3 | rates → house → claim issue |
| range | 2 | rates → claim range |
| court | 3 | rates → north → claim court |
| audio | 3 | rates → along → claim audio |
| light | 3 | rates → login → claim light |
| write | 3 | rates → their → claim write |
| offer | 3 | rates → would → claim offer |
| given | 3 | rates → women → claim given |
| files | 2 | rates → files |
| event | 3 | rates → white → claim event |
| needs | 2 | rates → needs |
| major | 3 | rates → march → claim major |
| areas | 3 | rates → years → claim areas |
| space | 2 | rates → claim space |
| cards | 2 | rates → claim cards |
| child | 3 | rates → would → claim child |
| enter | 2 | rates → claim enter |
| share | 2 | rates → claim share |
| added | 2 | rates → claim added |
| radio | 2 | rates → claim radio |
| until | 2 | rates → claim until |
| color | 3 | rates → world → claim color |
| track | 2 | rates → claim track |
| least | 3 | rates → state → claim least |
| trade | 3 | rates → great → claim trade |
| green | 4 | rates → would → never → claim green |
| close | 3 | rates → house → claim close |
| drive | 3 | rates → price → claim drive |
| short | 3 | rates → first → claim short |
| means | 2 | rates → means |
| daily | 2 | rates → claim daily |
| beach | 3 | rates → place → claim beach |
| costs | 3 | rates → posts → claim costs |
| style | 3 | rates → these → claim style |
| front | 3 | rates → north → claim front |
| parts | 2 | rates → claim parts |
| early | 3 | rates → large → claim early |
| miles | 3 | rates → files → claim miles |
| sound | 3 | rates → music → claim sound |
| works | 2 | rates → works |
| rules | 2 | rates → claim rules |
| final | 3 | rates → along → claim final |
| thing | 3 | rates → login → claim thing |
| cheap | 3 | rates → place → claim cheap |
| third | 3 | rates → north → claim third |
| gifts | 3 | rates → posts → claim gifts |
| cover | 3 | rates → would → claim cover |
| often | 3 | rates → hotel → claim often |
| watch | 2 | rates → claim watch |
| deals | 3 | rates → means → claim deals |
| words | 3 | rates → works → claim words |
| heart | 3 | rates → great → claim heart |
| error | 3 | rates → price → claim error |
| clear | 3 | rates → learn → claim clear |
| makes | 3 | rates → games → claim makes |
| taken | 2 | rates → claim taken |
| known | 3 | rates → would → claim known |
| cases | 4 | rates → games → sales → claim cases |
| quick | 3 | rates → would → claim quick |
| whole | 3 | rates → phone → claim whole |
| later | 3 | rates → water → claim later |
| basic | 2 | rates → claim basic |
| shows | 3 | rates → books → claim shows |
| along | 2 | rates → along |
| among | 3 | rates → along → claim among |
| speed | 2 | rates → claim speed |
| brand | 3 | rates → board → claim brand |
| stuff | 3 | rates → would → claim stuff |
| doing | 3 | rates → would → claim doing |
| loans | 3 | rates → class → claim loans |
| shoes | 3 | rates → files → claim shoes |
| entry | 2 | rates → claim entry |
| notes | 3 | rates → sites → claim notes |
| force | 3 | rates → price → claim force |
| river | 2 | rates → claim river |
| album | 3 | rates → along → claim album |
| views | 3 | rates → needs → claim views |
| plans | 3 | rates → class → claim plans |
| build | 3 | rates → would → claim build |
| types | 3 | rates → times → claim types |
| lines | 3 | rates → files → claim lines |
| apply | 3 | rates → along → claim apply |
| asked | 2 | rates → claim asked |
| cross | 3 | rates → works → claim cross |
| weeks | 3 | rates → needs → claim weeks |
| lower | 3 | rates → would → claim lower |
| union | 3 | rates → would → claim union |
| names | 3 | rates → games → claim names |
| leave | 3 | rates → place → claim leave |
| woman | 3 | rates → along → claim woman |
| cable | 3 | rates → value → claim cable |

</details>

## Depth 2 — `packs/wordle200/d2.py`

An attempt is an act the agent played: each guess, and the claim it ends on.

| attempts | answers |  |
|---|---|---|
| 1 | 1 | # |
| 2 | 72 | ####################### |
| 3 | 124 | ######################################## |
| 4 | 3 | # |

Failures: none — every answer was claimed right, or guessed all-green, within the horizon.

<details><summary>every answer</summary>

| answer | attempts | acts |
|---|---|---|
| about | 2 | rates → claim about |
| other | 2 | rates → other |
| which | 3 | rates → would → claim which |
| their | 2 | rates → their |
| there | 3 | rates → their → claim there |
| first | 2 | rates → first |
| would | 2 | rates → would |
| these | 2 | rates → these |
| click | 3 | rates → would → claim click |
| price | 2 | rates → price |
| state | 2 | rates → state |
| email | 3 | rates → place → claim email |
| world | 2 | rates → world |
| music | 2 | rates → music |
| after | 2 | rates → claim after |
| video | 3 | rates → women → claim video |
| where | 3 | rates → price → claim where |
| books | 2 | rates → books |
| links | 3 | rates → books → claim links |
| years | 2 | rates → years |
| order | 3 | rates → would → claim order |
| items | 2 | rates → claim items |
| group | 3 | rates → world → claim group |
| under | 3 | rates → would → claim under |
| games | 2 | rates → games |
| could | 3 | rates → would → claim could |
| great | 2 | rates → great |
| hotel | 2 | rates → hotel |
| store | 2 | rates → claim store |
| terms | 2 | rates → claim terms |
| right | 2 | rates → claim right |
| local | 3 | rates → along → claim local |
| those | 3 | rates → these → claim those |
| using | 3 | rates → music → claim using |
| phone | 2 | rates → phone |
| forum | 3 | rates → world → claim forum |
| based | 2 | rates → claim based |
| black | 3 | rates → along → claim black |
| check | 3 | rates → phone → claim check |
| index | 3 | rates → women → claim index |
| might | 2 | rates → might |
| house | 2 | rates → house |
| women | 2 | rates → women |
| south | 3 | rates → would → claim south |
| pages | 3 | rates → games → claim pages |
| found | 3 | rates → would → claim found |
| photo | 3 | rates → might → claim photo |
| power | 3 | rates → would → claim power |
| while | 3 | rates → phone → claim while |
| three | 3 | rates → other → claim three |
| total | 2 | rates → claim total |
| place | 2 | rates → place |
| think | 3 | rates → might → claim think |
| north | 2 | rates → north |
| posts | 2 | rates → posts |
| media | 3 | rates → place → claim media |
| water | 2 | rates → water |
| since | 3 | rates → house → claim since |
| guide | 3 | rates → phone → claim guide |
| board | 2 | rates → board |
| white | 2 | rates → white |
| small | 2 | rates → small |
| times | 2 | rates → times |
| sites | 2 | rates → sites |
| level | 3 | rates → women → claim level |
| hours | 3 | rates → works → claim hours |
| image | 3 | rates → place → claim image |
| title | 2 | rates → claim title |
| shall | 3 | rates → small → claim shall |
| class | 2 | rates → class |
| still | 3 | rates → would → claim still |
| money | 3 | rates → women → claim money |
| every | 3 | rates → price → claim every |
| visit | 3 | rates → would → claim visit |
| tools | 3 | rates → posts → claim tools |
| reply | 2 | rates → claim reply |
| value | 2 | rates → value |
| press | 2 | rates → press |
| learn | 2 | rates → learn |
| print | 3 | rates → north → claim print |
| stock | 3 | rates → would → claim stock |
| point | 3 | rates → might → claim point |
| sales | 3 | rates → games → sales |
| large | 2 | rates → large |
| table | 2 | rates → claim table |
| start | 2 | rates → claim start |
| model | 3 | rates → women → claim model |
| human | 3 | rates → along → claim human |
| movie | 3 | rates → phone → claim movie |
| march | 2 | rates → march |
| going | 3 | rates → would → claim going |
| study | 3 | rates → would → claim study |
| staff | 2 | rates → claim staff |
| again | 3 | rates → along → claim again |
| never | 3 | rates → would → never |
| users | 3 | rates → press → claim users |
| topic | 3 | rates → might → claim topic |
| below | 3 | rates → phone → claim below |
| party | 2 | rates → claim party |
| login | 3 | rates → would → claim login |
| legal | 3 | rates → place → claim legal |
| above | 3 | rates → place → claim above |
| quote | 3 | rates → white → claim quote |
| story | 3 | rates → first → claim story |
| rates | 1 | rates |
| young | 3 | rates → would → claim young |
| field | 3 | rates → phone → claim field |
| paper | 2 | rates → claim paper |
| night | 3 | rates → might → night |
| issue | 3 | rates → house → claim issue |
| range | 2 | rates → claim range |
| court | 3 | rates → north → claim court |
| audio | 3 | rates → along → claim audio |
| light | 4 | rates → might → night → claim light |
| write | 3 | rates → their → claim write |
| offer | 3 | rates → would → claim offer |
| given | 3 | rates → women → claim given |
| files | 2 | rates → files |
| event | 3 | rates → white → claim event |
| needs | 2 | rates → needs |
| major | 3 | rates → march → claim major |
| areas | 3 | rates → years → claim areas |
| space | 2 | rates → claim space |
| cards | 2 | rates → claim cards |
| child | 3 | rates → would → claim child |
| enter | 2 | rates → claim enter |
| share | 2 | rates → claim share |
| added | 2 | rates → claim added |
| radio | 2 | rates → claim radio |
| until | 2 | rates → claim until |
| color | 3 | rates → world → claim color |
| track | 2 | rates → claim track |
| least | 3 | rates → state → claim least |
| trade | 3 | rates → great → claim trade |
| green | 4 | rates → would → never → claim green |
| close | 3 | rates → house → claim close |
| drive | 3 | rates → price → claim drive |
| short | 3 | rates → first → claim short |
| means | 2 | rates → means |
| daily | 2 | rates → claim daily |
| beach | 3 | rates → place → claim beach |
| costs | 3 | rates → posts → claim costs |
| style | 3 | rates → these → claim style |
| front | 3 | rates → north → claim front |
| parts | 2 | rates → claim parts |
| early | 3 | rates → large → claim early |
| miles | 3 | rates → files → claim miles |
| sound | 3 | rates → music → claim sound |
| works | 2 | rates → works |
| rules | 2 | rates → claim rules |
| final | 3 | rates → along → claim final |
| thing | 3 | rates → might → claim thing |
| cheap | 3 | rates → place → claim cheap |
| third | 3 | rates → north → claim third |
| gifts | 3 | rates → posts → claim gifts |
| cover | 3 | rates → would → claim cover |
| often | 3 | rates → hotel → claim often |
| watch | 2 | rates → claim watch |
| deals | 3 | rates → means → claim deals |
| words | 3 | rates → works → claim words |
| heart | 3 | rates → great → claim heart |
| error | 3 | rates → price → claim error |
| clear | 3 | rates → learn → claim clear |
| makes | 3 | rates → games → claim makes |
| taken | 2 | rates → claim taken |
| known | 3 | rates → would → claim known |
| cases | 4 | rates → games → sales → claim cases |
| quick | 3 | rates → would → claim quick |
| whole | 3 | rates → phone → claim whole |
| later | 3 | rates → water → claim later |
| basic | 2 | rates → claim basic |
| shows | 3 | rates → books → claim shows |
| along | 2 | rates → along |
| among | 3 | rates → along → claim among |
| speed | 2 | rates → claim speed |
| brand | 3 | rates → board → claim brand |
| stuff | 3 | rates → would → claim stuff |
| doing | 3 | rates → would → claim doing |
| loans | 3 | rates → class → claim loans |
| shoes | 3 | rates → files → claim shoes |
| entry | 2 | rates → claim entry |
| notes | 3 | rates → sites → claim notes |
| force | 3 | rates → price → claim force |
| river | 2 | rates → claim river |
| album | 3 | rates → along → claim album |
| views | 3 | rates → needs → claim views |
| plans | 3 | rates → class → claim plans |
| build | 3 | rates → would → claim build |
| types | 3 | rates → times → claim types |
| lines | 3 | rates → files → claim lines |
| apply | 3 | rates → along → claim apply |
| asked | 2 | rates → claim asked |
| cross | 3 | rates → works → claim cross |
| weeks | 3 | rates → needs → claim weeks |
| lower | 3 | rates → would → claim lower |
| union | 3 | rates → would → claim union |
| names | 3 | rates → games → claim names |
| leave | 3 | rates → place → claim leave |
| woman | 3 | rates → along → claim woman |
| cable | 3 | rates → value → claim cable |

</details>

## Depth 1 + θ — `packs/wordle200/adaptive.py`

An attempt is an act the agent played: each guess, and the claim it ends on.

| attempts | answers |  |
|---|---|---|
| 1 | 1 | # |
| 2 | 72 | ####################### |
| 3 | 124 | ######################################## |
| 4 | 3 | # |

Failures: none — every answer was claimed right, or guessed all-green, within the horizon.

<details><summary>every answer</summary>

| answer | attempts | acts |
|---|---|---|
| about | 2 | rates → claim about |
| other | 2 | rates → other |
| which | 3 | rates → would → claim which |
| their | 2 | rates → their |
| there | 3 | rates → their → claim there |
| first | 2 | rates → first |
| would | 2 | rates → would |
| these | 2 | rates → these |
| click | 3 | rates → would → claim click |
| price | 2 | rates → price |
| state | 2 | rates → state |
| email | 3 | rates → place → claim email |
| world | 2 | rates → world |
| music | 2 | rates → music |
| after | 2 | rates → claim after |
| video | 3 | rates → women → claim video |
| where | 3 | rates → price → claim where |
| books | 2 | rates → books |
| links | 3 | rates → books → claim links |
| years | 2 | rates → years |
| order | 3 | rates → would → claim order |
| items | 2 | rates → claim items |
| group | 3 | rates → world → claim group |
| under | 3 | rates → would → claim under |
| games | 2 | rates → games |
| could | 3 | rates → would → claim could |
| great | 2 | rates → great |
| hotel | 2 | rates → hotel |
| store | 2 | rates → claim store |
| terms | 2 | rates → claim terms |
| right | 2 | rates → claim right |
| local | 3 | rates → along → claim local |
| those | 3 | rates → these → claim those |
| using | 3 | rates → music → claim using |
| phone | 2 | rates → phone |
| forum | 3 | rates → world → claim forum |
| based | 2 | rates → claim based |
| black | 3 | rates → along → claim black |
| check | 3 | rates → phone → claim check |
| index | 3 | rates → women → claim index |
| might | 2 | rates → might |
| house | 2 | rates → house |
| women | 2 | rates → women |
| south | 3 | rates → would → claim south |
| pages | 3 | rates → games → claim pages |
| found | 3 | rates → would → claim found |
| photo | 3 | rates → might → claim photo |
| power | 3 | rates → would → claim power |
| while | 3 | rates → phone → claim while |
| three | 3 | rates → other → claim three |
| total | 2 | rates → claim total |
| place | 2 | rates → place |
| think | 3 | rates → might → claim think |
| north | 2 | rates → north |
| posts | 2 | rates → posts |
| media | 3 | rates → place → claim media |
| water | 2 | rates → water |
| since | 3 | rates → house → claim since |
| guide | 3 | rates → phone → claim guide |
| board | 2 | rates → board |
| white | 2 | rates → white |
| small | 2 | rates → small |
| times | 2 | rates → times |
| sites | 2 | rates → sites |
| level | 3 | rates → women → claim level |
| hours | 3 | rates → works → claim hours |
| image | 3 | rates → place → claim image |
| title | 2 | rates → claim title |
| shall | 3 | rates → small → claim shall |
| class | 2 | rates → class |
| still | 3 | rates → would → claim still |
| money | 3 | rates → women → claim money |
| every | 3 | rates → price → claim every |
| visit | 3 | rates → would → claim visit |
| tools | 3 | rates → posts → claim tools |
| reply | 2 | rates → claim reply |
| value | 2 | rates → value |
| press | 2 | rates → press |
| learn | 2 | rates → learn |
| print | 3 | rates → north → claim print |
| stock | 3 | rates → would → claim stock |
| point | 3 | rates → might → claim point |
| sales | 3 | rates → games → sales |
| large | 2 | rates → large |
| table | 2 | rates → claim table |
| start | 2 | rates → claim start |
| model | 3 | rates → women → claim model |
| human | 3 | rates → along → claim human |
| movie | 3 | rates → phone → claim movie |
| march | 2 | rates → march |
| going | 3 | rates → would → claim going |
| study | 3 | rates → would → claim study |
| staff | 2 | rates → claim staff |
| again | 3 | rates → along → claim again |
| never | 3 | rates → would → never |
| users | 3 | rates → press → claim users |
| topic | 3 | rates → might → claim topic |
| below | 3 | rates → phone → claim below |
| party | 2 | rates → claim party |
| login | 3 | rates → would → claim login |
| legal | 3 | rates → place → claim legal |
| above | 3 | rates → place → claim above |
| quote | 3 | rates → white → claim quote |
| story | 3 | rates → first → claim story |
| rates | 1 | rates |
| young | 3 | rates → would → claim young |
| field | 3 | rates → phone → claim field |
| paper | 2 | rates → claim paper |
| night | 3 | rates → might → night |
| issue | 3 | rates → house → claim issue |
| range | 2 | rates → claim range |
| court | 3 | rates → north → claim court |
| audio | 3 | rates → along → claim audio |
| light | 4 | rates → might → night → claim light |
| write | 3 | rates → their → claim write |
| offer | 3 | rates → would → claim offer |
| given | 3 | rates → women → claim given |
| files | 2 | rates → files |
| event | 3 | rates → white → claim event |
| needs | 2 | rates → needs |
| major | 3 | rates → march → claim major |
| areas | 3 | rates → years → claim areas |
| space | 2 | rates → claim space |
| cards | 2 | rates → claim cards |
| child | 3 | rates → would → claim child |
| enter | 2 | rates → claim enter |
| share | 2 | rates → claim share |
| added | 2 | rates → claim added |
| radio | 2 | rates → claim radio |
| until | 2 | rates → claim until |
| color | 3 | rates → world → claim color |
| track | 2 | rates → claim track |
| least | 3 | rates → state → claim least |
| trade | 3 | rates → great → claim trade |
| green | 4 | rates → would → never → claim green |
| close | 3 | rates → house → claim close |
| drive | 3 | rates → price → claim drive |
| short | 3 | rates → first → claim short |
| means | 2 | rates → means |
| daily | 2 | rates → claim daily |
| beach | 3 | rates → place → claim beach |
| costs | 3 | rates → posts → claim costs |
| style | 3 | rates → these → claim style |
| front | 3 | rates → north → claim front |
| parts | 2 | rates → claim parts |
| early | 3 | rates → large → claim early |
| miles | 3 | rates → files → claim miles |
| sound | 3 | rates → music → claim sound |
| works | 2 | rates → works |
| rules | 2 | rates → claim rules |
| final | 3 | rates → along → claim final |
| thing | 3 | rates → might → claim thing |
| cheap | 3 | rates → place → claim cheap |
| third | 3 | rates → north → claim third |
| gifts | 3 | rates → posts → claim gifts |
| cover | 3 | rates → would → claim cover |
| often | 3 | rates → hotel → claim often |
| watch | 2 | rates → claim watch |
| deals | 3 | rates → means → claim deals |
| words | 3 | rates → works → claim words |
| heart | 3 | rates → great → claim heart |
| error | 3 | rates → price → claim error |
| clear | 3 | rates → learn → claim clear |
| makes | 3 | rates → games → claim makes |
| taken | 2 | rates → claim taken |
| known | 3 | rates → would → claim known |
| cases | 4 | rates → games → sales → claim cases |
| quick | 3 | rates → would → claim quick |
| whole | 3 | rates → phone → claim whole |
| later | 3 | rates → water → claim later |
| basic | 2 | rates → claim basic |
| shows | 3 | rates → books → claim shows |
| along | 2 | rates → along |
| among | 3 | rates → along → claim among |
| speed | 2 | rates → claim speed |
| brand | 3 | rates → board → claim brand |
| stuff | 3 | rates → would → claim stuff |
| doing | 3 | rates → would → claim doing |
| loans | 3 | rates → class → claim loans |
| shoes | 3 | rates → files → claim shoes |
| entry | 2 | rates → claim entry |
| notes | 3 | rates → sites → claim notes |
| force | 3 | rates → price → claim force |
| river | 2 | rates → claim river |
| album | 3 | rates → along → claim album |
| views | 3 | rates → needs → claim views |
| plans | 3 | rates → class → claim plans |
| build | 3 | rates → would → claim build |
| types | 3 | rates → times → claim types |
| lines | 3 | rates → files → claim lines |
| apply | 3 | rates → along → claim apply |
| asked | 2 | rates → claim asked |
| cross | 3 | rates → works → claim cross |
| weeks | 3 | rates → needs → claim weeks |
| lower | 3 | rates → would → claim lower |
| union | 3 | rates → would → claim union |
| names | 3 | rates → games → claim names |
| leave | 3 | rates → place → claim leave |
| woman | 3 | rates → along → claim woman |
| cable | 3 | rates → value → claim cable |

</details>

### The think act

The pack declares Depth⁺ 2, a Fraction f = 1/2, a fitted Cost table and a
Rate r = 1/10000000. At every step `decide⁺` settles into one of S7's four buckets, in
precedence order, and only the last of them costs anything.

| bucket | steps | share | what it means |
|---|---|---|---|
| `struck_n` | 0 | 0.0% | n ≤ d, or no guess left: there is nothing a deeper look could reach |
| `struck_cap` | 158 | 29.9% | the cap leaves less room than the thought costs; f is never read |
| `refused` | 0 | 0.0% | Q(θ) was formed and θ still lost |
| **`think`** | **371** | 70.1% | **θ bought: one deeper look, paid for, and the act it found is played** |
| **total steps** | **529** |  |  |

**Wrong claims**: 0 of 200. A wrong claim is the horizon running out, not a mistake the
kernel made: `decide` plays the act of highest value at the depth it is allowed, and when
no guess left in the menu can separate the candidates in the steps remaining, claiming one
of them is the best act there is.

**Thought paid**, over all 200 episodes: 44435183993453775285411297/183306030446682985000000 (≈ 242.4098) of utility,
which is 44435183993453775285411297/36661206089336597000000000 (≈ 1.212049) an episode. It is not a price: no act was
executed for it, the door never saw it, and it consumed no horizon (C17).

### Predicted against realised operations (E6)

The Cost table says how many operations a thought at s live states will take. The kernel
counts what it actually took, and the two are printed side by side and never compared by
anything: the prediction is what the policy is charged for, the count is a measurement.

| s (live states) | thoughts | ops predicted | counted, least | counted, most | counted 0 |
|---|---|---|---|---|---|
| 2 | 36 | 1,300 | 0 | 1,882 | 18 |
| 3 | 27 | 2,925 | 0 | 3,441 | 18 |
| 4 | 20 | 5,199 | 0 | 6,100 | 15 |
| 5 | 5 | 8,121 | 0 | 7,367 | 4 |
| 6 | 18 | 11,690 | 0 | 11,914 | 15 |
| 7 | 7 | 15,906 | 0 | 11,990 | 6 |
| 8 | 24 | 20,768 | 0 | 23,180 | 21 |
| 9 | 9 | 26,275 | 0 | 23,466 | 8 |
| 11 | 11 | 39,223 | 0 | 38,430 | 10 |
| 14 | 14 | 63,468 | 0 | 44,196 | 13 |
| 200 | 200 | 12,107,255 | 0 | 12,107,256 | 199 |

Over all 371 thoughts the kernel counted 12,404,006 operations, against 2,424,098,317 predicted —
about 1% of the Cost table's number, and 327 of the thoughts counted nothing at all.

That is the memo of brief 004 and not a fault in the fit. A thought is one evaluation of
one belief at depth 2, and the World keeps what it has already worked out; the first
thought at a node pays for it and every later thought at **that same node** finds the
answer there. The rows above group by s, the count of live states the Cost is keyed on,
and two different nodes can have the same s — which is why the least and the most in a
row differ, and why the `counted 0` column is the memo and not the model. The page
expects this: two evaluators may count differently, and each prints its own count
beside the same prediction (E6). The policy is charged the prediction, always, and never
the count (J15) — so nothing the memo saves ever reaches a value.


### The five curves of E3

Computed by `tools/curves.py` over the declared model — exactly, in rationals, over every
answer — from this kernel's own acts: `decide` gives the act at a depth, `decide⁺` gives
the bucket and the charge, and the tool does the expectation and the backward induction.
`laws/kit_wordle_think.py` prints the same table from the author's oracle, and the two
agree to every digit printed here.

Utility per episode. **Larger is better**; a guess costs 1, a wrong claim -7.

| r | fixed d=1 | always d=2 | best fixed | **adaptive** | omniscient |
|---|---|---|---|---|---|
| `0` | -2.6450 | -2.6450 | -2.6450 | -2.6450 | -2.6450 |
| `1/100000000` | -2.6450 | -2.7662 | -2.6450 | -2.7662 | -2.6450 |
| `3/100000000` | -2.6450 | -3.0086 | -2.6450 | -3.0086 | -2.6450 |
| `1/10000000` **←** | -2.6450 | -3.8571 | -2.6450 | -3.8570 | -2.6450 |
| `3/10000000` | -2.6450 | -6.2812 | -2.6450 | -2.6490 | -2.6450 |
| `1/1000000` | -2.6450 | -14.7657 | -2.6450 | -2.6582 | -2.6450 |

**Regret at the declared rate** r = 1/10000000:

- against the omniscient meta-policy: **1.2120** of utility per episode.
- against the best fixed depth in hindsight: **1.2120**.
- against thinking never (fixed d = 1): **1.2120**,
  and the thought it paid for was 1.2120 an episode.

Those last two are the same number, and that is the whole finding on this lexicon:
**every thought the agent bought changed nothing.** It played the same acts as the
shallow agent — the same mean attempts, answer for answer — and the entire loss is
what it paid to discover that the second look agreed with the first. The Fraction is
the owner's optimism about a look it has not taken yet (f = 1/2), and here the
optimism was misplaced; the cap could not tell, because the cap is a bound and not a
deliberation (C19). Further up the grid the Cost table finally makes c large enough for
the cap to strike θ, and the curve comes back to within a few thousandths of the
shallow one.

