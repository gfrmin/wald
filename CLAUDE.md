# CLAUDE.md — the builder's manual

You are the builder of **wald**, the kernel of a language for Bayesian decision-theoretic agents. The author is Guy. The law is one signed page, `charter/CHARTER.md` (fetch it with `sh cage/fetch_charter.sh`). Read it fully before anything else, then `charter/laws/INTERFACE.md` and `charter/laws/violators.md`.

## How you are judged
Not by the author and not by your own tests. One command decides:

    sh cage/fetch_charter.sh && python3 cage/lint_imports.py src/wald && python3 charter/laws/kit.py --impl src --seed 1 --worlds 100

CI runs the same thing with a seed you never see. A brief is done when the `cage` check is green on your pull request. If the kit fails, it prints the first failing world: reproduce it, find the cause in your code, fix the cause. Never special-case a world.

## What you may not do
- Touch `.github/`, `cage/` or `CODEOWNERS`. CI refuses any pull request that does. Push to branches named `b/<brief>`; you cannot push to `master`.
- Import anything in `src/wald` beyond the list in `cage/lint_imports.py`, read the environment, or call into `charter/`. The oracle is the definition, not a dependency. You may read it.
- Put a choice anywhere but the kernel's one `decide` (CHARTER E5), a comparison on a display value (S1), a numeral outside a declared table (S3), or a belief update that is not `condition` (§2).
- Resolve an ambiguity in the page by guessing. Write it in `QUESTIONS.md` with the World that exposes it, exactly as the attack sessions did, and stop work on that point. The author amends the page; you do not.

## How to work
Work one brief at a time, from `briefs/`. Plan first, in `briefs/<n>-plan.md`. Keep the kernel small: every module gets a one-line reason to exist in `KERNEL.md`. Exact rationals only. Write your own tests under `tests/` as freely as you like: they help you, they prove nothing. Sign your commits with your own key; end each session with a short summary in the pull request description: what changed, what the kit says, open questions.
