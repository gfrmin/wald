# Wordle — scoreboard

`packs/wordle200/d1.py`, `packs/wordle200/d2.py`, played by `wald.episode.run` through a door that answers
with the game's feedback. Every act is the kernel's own: the depth below is what the pack
declares, and the kernel plays `decide_min(d, n)` (CHARTER E3).

|  | **depth 1** | **depth 2** |
|---|---|---|
| words (states) | 200 | 200 |
| horizon | 5 | 5 |
| **declared depth** | **1** | **2** |
| answers played | 200 | 200 |
| solved | 200 / 200 | 200 / 200 |
| **mean attempts** | **2.645** | **2.645** |
| worst | 4 | 4 |
| first episode | 1.8 s | 33.0 s |
| all answers | 2.2 s | 46.3 s |

**The price of the floor, measured.** Mean attempts at depth 1 minus mean attempts at depth 2, over all 200 answers, is **0.000**. Nothing here is tuned to make it larger: the two packs differ in one line.

The two depths are not playing the same game, though. They play 8 of the 200 answers differently: `might`, `photo`, `think`, `point`, `topic`, `night`, `light`, `thing`. Of those, the
deeper agent needs fewer attempts on 1 and more on 1.

## Quantities by source

`wald.surface.census`, which counts quantities, not numerals: each cell, parameter,
mixture weight, price, the horizon and the depth once, however it is written.

| source | depth 1 | depth 2 |
|---|---|---|
| data | 40401 | 40401 |
| elicited | 80002 | 80002 |
| fitted | 0 | 0 |
| **total** | **120403** | **120403** |

`fitted` is 0: nothing in this World is a point estimate. The prior, the prices, the
horizon and every kernel row are `data` — facts of the game and of the word list. What is
`elicited` is the owner's: the depth, and the utilities, including `loss`.

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
