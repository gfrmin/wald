# Brief 001b — make kit v0.2 green

**Done when** the `cage` check is green on a pull request from `b/001b-table-shape`.

Kit v0.2 (now locked in `cage/charter.lock`) adds what brief 001 showed the kit was missing. Your three findings from brief 001 are adopted: C1 is contracted only for outcomes of positive mass and the generator now draws zero kernel entries; `PRICE` is an official refusal name; a `fresh` act naming a non-component source is `SHARED_SOURCE`.

One thing is new to you. `wald.world.declare` must refuse, by the name `TABLE_SHAPE`:
- a utility table that is not total over Ω (a terminal act missing a state, or naming a state not in Ω);
- a kernel that is not total over Ω;
- an ending outcome that its act's kernel cannot emit;
- a u_end table that is not total over Ω.

Read the new text in `charter/laws/INTERFACE.md`. Nothing else changes. If you think any of the four cases is lawful under the page, say so in `QUESTIONS.md` with the World that shows it, and stop.
