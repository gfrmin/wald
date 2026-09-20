"""The Wordle pack: that it is the game, and that the kernel plays it.

The kit checks the pack against a feedback rule it computes itself. These tests check the rule
where the word list is thin (the list has no doubled letters to speak of, and duplicate handling
is exactly where a feedback rule goes wrong), that the generator's output is the committed pack,
and that the World the pack declares is the one the brief describes."""
import pathlib
import sys
import unittest
from fractions import Fraction as F

import _path  # noqa: F401

ROOT = pathlib.Path(_path.ROOT)
sys.path.insert(0, str(ROOT / "tools"))

from make_wordle_pack import ALL_GREEN, LOSS, feedback, pack     # noqa: E402
from wald import belief as B                                     # noqa: E402
from wald.decide import decide, value                            # noqa: E402
from wald.episode import Door, run                               # noqa: E402
from wald.surface import census, check                           # noqa: E402
from wald.world import declare                                   # noqa: E402

PACK = ROOT / "packs" / "wordle" / "pack.py"
WORDS = (ROOT / "charter" / "laws" / "wordle" / "words.txt")


class Feedback(unittest.TestCase):
    """Greens first, then yellows while unmatched copies of the letter remain."""

    def test_all_green_and_all_grey(self):
        self.assertEqual(feedback("about", "about"), "ggggg")
        self.assertEqual(feedback("abcde", "fghij"), "-----")

    def test_a_letter_in_the_wrong_place(self):
        self.assertEqual(feedback("abcde", "edcba"), "yygyy")

    def test_a_doubled_guess_letter_when_the_answer_has_one(self):
        "The leftmost copy takes the single mark; the second gets nothing."
        self.assertEqual(feedback("speed", "abide"), "--y-y")
        self.assertEqual(feedback("llama", "hello"), "yy---")

    def test_greens_are_taken_before_yellows(self):
        """`koala` has one l, and no green claims it, so the first l of `llama` is yellow and the
        second is not; both a's are green."""
        self.assertEqual(feedback("llama", "koala"), "y-g-g")

    def test_a_green_spends_the_copy_a_yellow_would_have_taken(self):
        "Both e's of `these` are matched green, so the leading e of `geese` earns nothing."
        self.assertEqual(feedback("geese", "these"), "--ggg")
        self.assertEqual(feedback("eerie", "there"), "y-y-g")

    def test_a_doubled_answer_letter_marks_two_copies(self):
        self.assertEqual(feedback("sells", "belle"), "-ggg-")

    def test_the_rule_is_symmetric_only_in_all_green(self):
        self.assertNotEqual(feedback("about", "other"), feedback("other", "about"))
        for w in ("about", "index"):
            self.assertEqual(feedback(w, w), ALL_GREEN)


class TheCommittedPack(unittest.TestCase):
    def setUp(self):
        self.words = WORDS.read_text(encoding="utf-8").split() if WORDS.is_file() else None
        self.text = PACK.read_text(encoding="utf-8")
        self.spec = check(self.text, data_dir=str(PACK.parent))

    @unittest.skipIf(not WORDS.is_file(), "charter not fetched")
    def test_the_generator_reproduces_the_committed_pack(self):
        "The pack is generated: if the generator and the file disagree, one of them is stale."
        self.assertEqual(pack(self.words), self.text)

    def test_the_states_are_the_words_in_order(self):
        self.assertEqual(len(self.spec["prior"]), 40)
        if self.words:
            self.assertEqual(list(self.spec["prior"]), self.words)

    def test_the_prior_is_uniform(self):
        for p in self.spec["prior"].values():
            self.assertEqual(p, F(1, 40))

    def test_every_word_is_a_once_guess_at_price_one(self):
        for word, act in self.spec["O"].items():
            self.assertIs(act["once"], True, word)
            self.assertEqual(act["price"], F(1), word)

    def test_all_green_ends_the_episode_at_zero(self):
        for word, act in self.spec["O"].items():
            self.assertEqual(set(act["ends"]), {ALL_GREEN}, word)
            self.assertEqual(set(act["ends"][ALL_GREEN].values()), {F(0)}, word)

    def test_every_kernel_row_is_the_feedback_of_that_guess(self):
        for guess, act in self.spec["O"].items():
            for answer, row in act["K"].items():
                alive = {o: p for o, p in row.items() if p != 0}
                self.assertEqual(alive, {feedback(guess, answer): F(1)}, (guess, answer))

    def test_the_terminal_acts_are_the_claims(self):
        self.assertEqual(list(self.spec["T"]), ["claim " + w for w in self.spec["prior"]])
        for word in self.spec["prior"]:
            u = self.spec["T"]["claim " + word]
            self.assertEqual(u[word], F(-1))
            self.assertEqual({v for s, v in u.items() if s != word}, {F(LOSS)})

    def test_a_wrong_claim_is_worse_than_playing_the_game_out(self):
        "Five guesses and a claim cost 6; the kit asks for a loss below -6."
        self.assertLess(LOSS, -(self.spec["N"] + 1))

    def test_the_clock_and_the_stance(self):
        self.assertEqual(self.spec["N"], 5)
        self.assertEqual(self.spec["d"], 1)
        self.assertIs(self.spec["closed"], True)

    def test_nothing_is_fitted(self):
        self.assertEqual(census(self.text, data_dir=str(PACK.parent))["fitted"], 0)

    def test_the_pack_is_a_world(self):
        declare(self.spec)


class Game(Door):
    def __init__(self, answer):
        self.answer = answer
        self.fired = None

    def outcome(self, act):
        return feedback(act, self.answer)

    def fire(self, act):
        self.fired = act


class Playing(unittest.TestCase):
    """The claims are not decoration: without them the World is degenerate at depth 1."""

    @classmethod
    def setUpClass(cls):
        cls.spec = check(PACK.read_text(encoding="utf-8"), data_dir=str(PACK.parent))
        cls.world = declare(cls.spec)

    def test_the_agent_looks_before_it_claims(self):
        b = B.prior(self.world)
        self.assertIn(decide(b, self.world, 1, frozenset()), self.spec["O"])

    def test_with_one_candidate_left_it_claims_rather_than_guesses(self):
        "Claiming the known word and guessing it are both worth -1; J3 gives the tie to the claim."
        word = list(self.spec["prior"])[0]
        certain = B._sealed({s: F(1 if s == word else 0) for s in self.spec["prior"]})
        self.assertEqual(value(certain, self.world, 0), F(-1))
        self.assertEqual(value(certain, self.world, 1), F(-1))
        self.assertEqual(decide(certain, self.world, 1, frozenset()), "claim " + word)

    def test_a_world_whose_only_terminal_act_is_giving_up_stops_at_once(self):
        """The brief's point 3, as arithmetic rather than as a workaround: the agent gives up,
        the oracle agrees, and the fix is in the World, not in the code."""
        give_up = dict(self.spec)
        give_up["T"] = {"give up": {s: F(LOSS) for s in self.spec["prior"]}}
        world = declare(give_up)
        self.assertEqual(decide(B.prior(world), world, 1, frozenset()), "give up")

    def test_two_answers_end_the_way_the_game_should(self):
        for answer in list(self.spec["prior"])[:2]:
            door = Game(answer)
            result = run(self.world, door)
            self.assertLessEqual(len(result.acts), self.spec["N"] + 1)
            if result.status == "ENDED":
                self.assertEqual(result.acts[-1], answer)
            else:
                self.assertEqual(door.fired, "claim " + answer)
