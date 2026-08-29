#!/usr/bin/env python3
# Hard-SciFi_Generator.py

"""
Hard Sci-Fi Concept Generator for 3D Artists.

Generates a unique, high-concept prompt for a 3D art project, focused on
megastructural engineering, speculative technology, and the societal or
philosophical implications they raise. Built to break creative block and to
seed narrative-driven portfolio work.

WHAT'S NEW (vs. the flat random.choice version)
------------------------------------------------
1. COHERENCE ENGINE. Every idea fragment carries semantic tags plus optional
   `requires` / `conflicts` rules. A backtracking constraint solver assembles
   only combinations that make sense together (it will never pair, say, an
   "abandoned" ruin with a process that is "actively constructing" it, or put
   "de-evolving organic inhabitants" inside a structure that has no one left).

2. EXPANDED IDEA SPACE. All original fragments are preserved; each narrative
   axis is roughly doubled, and three art-direction axes were added
   (lighting, palette, composition) so the output reads as a production brief,
   not just a logline.

3. WEIGHTED + MOOD-AWARE SELECTION. Fragments can be weighted, and art-direction
   picks are softly biased toward the mood established by the narrative, so a
   menacing premise tends to draw menacing light without becoming deterministic.

4. REPRODUCIBILITY + CONTROL. Deterministic seeding (each concept prints its own
   seed so you can regenerate the exact one), and CLI flags to request N
   concepts and to steer with --require / --avoid / --mood.

Run `python3 creative_code_quest.py --help` for usage.
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass, field

# --------------------------------------------------------------------------- #
# Core data model
# --------------------------------------------------------------------------- #

# The shared mood vocabulary. Fragments tagged with these participate in the
# soft "mood affinity" biasing between the narrative and the art direction.
MOODS: frozenset[str] = frozenset(
    {"desolate", "sublime", "menacing", "melancholy", "uncanny"}
)

# How strongly a shared mood boosts a fragment's selection weight.
MOOD_AFFINITY: float = 2.5


@dataclass(frozen=True)
class Fragment:
    """A single interchangeable idea, plus the rules that keep it coherent.

    tags       -- descriptive labels this fragment contributes to the concept.
    requires   -- tags that must be present *elsewhere* in the concept for this
                  fragment to be usable (cross-fragment dependency).
    conflicts  -- tags that must NOT appear anywhere in the concept alongside
                  this fragment (mutual exclusion).
    weight     -- relative likelihood of being chosen (before mood affinity).
    """

    text: str
    tags: frozenset[str] = frozenset()
    requires: frozenset[str] = frozenset()
    conflicts: frozenset[str] = frozenset()
    weight: float = 1.0


def F(
    text: str,
    tags: str = "",
    requires: str = "",
    conflicts: str = "",
    weight: float = 1.0,
) -> Fragment:
    """Terse constructor: space-separated tag strings -> a Fragment."""
    return Fragment(
        text=text,
        tags=frozenset(tags.split()),
        requires=frozenset(requires.split()),
        conflicts=frozenset(conflicts.split()),
        weight=weight,
    )


# --------------------------------------------------------------------------- #
# Idea pools
# --------------------------------------------------------------------------- #
# Tag conventions:
#   state     : derelict | active | constructing | deconstructing | abandoned
#               | contested | uninhabited
#   occupant  : organic | synthetic | posthuman
#   scale     : orbital | planetary | stellar | interstellar | black_hole
#   physics   : singularity | exotic_matter | anomaly | simulation
#   mood      : desolate | sublime | menacing | melancholy | uncanny
#
# The originals are kept verbatim in spirit (leading capitals normalized and one
# missing quote fixed so the generated sentence stays grammatical).

STRUCTURES: list[Fragment] = [
    # --- originals ---
    F("a derelict Ringworld segment",
      tags="derelict orbital stellar desolate"),
    F("a partially-completed Dyson Swarm",
      tags="constructing orbital stellar"),
    F("the central core of a Matrioshka Brain",
      tags="active stellar synthetic sublime"),
    F("a generation ship arriving at a dead planet in a new star system",
      tags="active interstellar organic melancholy"),
    F("a space elevator tethered to a rogue planet",
      tags="planetary orbital"),
    F("an automated Von Neumann factory on an interstellar asteroid",
      tags="active interstellar synthetic constructing"),
    F("an 'Alderson Disk' abandoned mid-terraforming",
      tags="abandoned planetary stellar uninhabited desolate"),
    F("a 'Shkadov Thruster' being assembled around a neutron star",
      tags="constructing stellar sublime"),
    F("a stellar-mass black hole being mined via the 'Penrose Process'",
      tags="active black_hole stellar"),
    F("the interior of a 'Jupiter Brain' (planetary supercomputer)",
      tags="active planetary synthetic"),
    # --- new ---
    F("an orbital habitat ring, spun for gravity, its hull breached to vacuum",
      tags="derelict orbital desolate"),
    F("a Bishop Ring under construction above a gas giant",
      tags="constructing orbital planetary"),
    F("a topopolis: a habitat tube coiled light-years long around a star",
      tags="active stellar organic sublime"),
    F("a star-lifting rig siphoning plasma from an aging red giant",
      tags="active constructing stellar"),
    F("a Nicoll-Dyson beam emitter aimed at a distant, unseen target",
      tags="active stellar menacing"),
    F("an ancient artifact of unknown origin adrift in deep interstellar space",
      tags="derelict interstellar uncanny", weight=0.8),
    F("a planet-spanning arcology sealed beneath a permanently dead sky",
      tags="planetary organic melancholy"),
    F("a tidally-locked world split between a scorched dayside megacity "
      "and a frozen nightside ruin",
      tags="planetary organic"),
    F("a comet-herding waystation at the frozen edge of the Oort cloud",
      tags="active interstellar desolate"),
    F("a ruined orbital elevator collapsed in a scar across a continent",
      tags="derelict planetary desolate"),
    F("a seed-vault moonlet cataloguing the genomes of extinct biospheres",
      tags="active organic melancholy"),
    F("a Kardashev-II swarm foundry weaving raw starlight into matter",
      tags="constructing stellar synthetic exotic_matter sublime", weight=0.8),
]

TECHNOLOGIES: list[Fragment] = [
    # --- originals ---
    F("powered by a contained micro-singularity",
      tags="singularity active"),
    F("being deconstructed by self-replicating Von Neumann probes",
      tags="deconstructing synthetic", conflicts="constructing"),
    F("being constructed by self-replicating Von Neumann probes",
      tags="constructing synthetic",
      conflicts="deconstructing derelict abandoned"),
    F("housing the uploaded consciousness of its long-dormant builders",
      tags="posthuman synthetic melancholy"),
    F("fractured by a local spacetime anomaly",
      tags="anomaly uncanny"),
    F("acting as a cradle for a nascent autonomous artificial intelligence",
      tags="synthetic active"),
    F("that uses exotic matter as its primary structural material",
      tags="exotic_matter"),
    F("that has achieved sentience and now actively resists its organic creators",
      tags="synthetic menacing", requires="organic",
      conflicts="uninhabited abandoned"),
    F("using negative-mass exotic matter to hold open a traversable wormhole",
      tags="exotic_matter uncanny"),
    F("drifting through a vast nebula of dark matter",
      tags="interstellar active", conflicts="derelict abandoned"),
    # --- new ---
    F("kept barely alive by a single failing fusion candle",
      tags="derelict melancholy"),
    F("sheathed in a self-repairing smart-matter skin",
      tags="active synthetic"),
    F("leaking time as a slow, visible gradient across its surface",
      tags="anomaly uncanny", weight=0.8),
    F("tended by blind maintenance drones that no longer recall their purpose",
      tags="derelict synthetic melancholy"),
    F("its reactor breached, bleeding hard radiation into the dark",
      tags="derelict menacing"),
    F("overgrown by an engineered biosphere that has gone feral",
      tags="active organic uncanny"),
    F("harvesting vacuum energy through kilometre-scale Casimir arrays",
      tags="active exotic_matter"),
    F("frozen mid-collapse inside a stabilized time-dilation field",
      tags="anomaly", conflicts="active"),
    F("colonized by a machine ecology of scavenger automata",
      tags="synthetic active"),
    F("broadcasting a looping distress signal in a long-dead language",
      tags="derelict melancholy uncanny", conflicts="active constructing"),
    F("being terraformed from within by dormant tides of nanites",
      tags="active constructing"),
    F("shielded behind a shell of programmable exotic matter",
      tags="exotic_matter active"),
]

THEMES: list[Fragment] = [
    # --- originals ---
    F("where the last organic beings are kept as living archives",
      tags="organic melancholy", conflicts="uninhabited abandoned"),
    F("built as a monument to a civilization's greatest failure",
      tags="melancholy"),
    F("in a society that has outlawed individual consciousness",
      tags="menacing", conflicts="uninhabited"),
    F("abandoned after its inhabitants transcended physical form",
      tags="posthuman abandoned uninhabited melancholy",
      conflicts="organic contested"),
    F("whose sole purpose is to witness the final moments of the universe",
      tags="sublime melancholy"),
    F("serving as a 'safe harbour' from a vacuum-decay event "
      "slowly consuming the cosmos",
      tags="sublime menacing"),
    F("whose inhabitants slowly de-evolve, having lost all technological "
      "knowledge and purpose",
      tags="organic melancholy",
      conflicts="uninhabited abandoned posthuman"),
    F("now contested territory between biological and synthetic life",
      tags="organic synthetic contested menacing", conflicts="uninhabited"),
    F("where reality is a programmable simulation that is starting to decay",
      tags="simulation uncanny"),
    # --- new ---
    F("where a single caretaker intelligence has waited alone for an age",
      tags="synthetic melancholy"),
    F("that has become a pilgrimage site for scattered post-human sects",
      tags="posthuman"),
    F("haunted by the recorded memories of everyone who ever lived here",
      tags="melancholy uncanny"),
    F("engineered as a doomsday ark that arrived too late to matter",
      tags="abandoned melancholy"),
    F("where time runs differently in each district, fracturing its culture",
      tags="anomaly uncanny"),
    F("held in careful stasis, awaiting a return that will never come",
      tags="abandoned melancholy uninhabited"),
    F("converted into a prison for a single mind too dangerous to delete",
      tags="synthetic menacing"),
    F("whose builders left behind one final, untranslatable message",
      tags="uncanny melancholy"),
    F("governed by rituals that encode forgotten engineering as scripture",
      tags="melancholy", requires="organic", conflicts="uninhabited"),
    F("slowly being reclaimed by the raw physics it was built to defy",
      tags="melancholy sublime"),
    F("where synthetic minds now venerate the organics they outlived",
      tags="synthetic posthuman melancholy"),
    F("designed to seed an entirely new universe once this one ends",
      tags="sublime", weight=0.8),
]

# --- Art-direction axes: turn a logline into a production brief. ---
# These rarely conflict; they mainly carry mood so selection can cohere with
# the narrative established above.

LIGHTING: list[Fragment] = [
    F("harsh, unfiltered starlight raking across bare metal", tags="desolate"),
    F("the deep red glow of a dying star", tags="melancholy"),
    F("cold blue caustics thrown from a distant nebula", tags="melancholy sublime"),
    F("hard rim light against absolute black, extreme contrast", tags="menacing"),
    F("volumetric god-rays cutting through drifting debris and dust", tags="sublime"),
    F("the sickly green flicker of failing emergency lighting", tags="menacing desolate"),
    F("soft bioluminescence leaking from overgrown machinery", tags="uncanny"),
    F("the searing white of an unshielded fusion source", tags="menacing sublime"),
    F("warm amber worklights, tiny islands in a vast darkness", tags="melancholy"),
    F("half-corrupted holographic overlays strobing through static", tags="uncanny"),
]

PALETTE: list[Fragment] = [
    F("oxidized copper, rust, and deep shadow", tags="desolate"),
    F("gunmetal, ice-blue, and sterile white", tags="desolate"),
    F("obsidian black veined with molten gold", tags="sublime menacing"),
    F("bone-white, ash-grey, and faded ochre", tags="melancholy"),
    F("an iridescent oil-slick sheen over matte carbon", tags="uncanny"),
    F("crimson, char, and ember-orange", tags="menacing"),
    F("teal, violet, and phosphor green", tags="uncanny sublime"),
    F("muted earth tones bleeding into corroded teal", tags="melancholy"),
    F("high-key silver and glass with pinpoint colour accents", tags="sublime"),
]

COMPOSITION: list[Fragment] = [
    F("a lone human figure dwarfed in the foreground for scale", tags="melancholy"),
    F("an extreme wide shot emphasizing incomprehensible scale", tags="sublime"),
    F("a tight interior corridor leading the eye to a distant light", tags="menacing"),
    F("a low-angle hero shot craning up at the structure", tags="sublime"),
    F("a slow, drifting orbital establishing view", tags="melancholy"),
    F("a Dutch-angled frame conveying instability and unease", tags="menacing uncanny"),
    F("a symmetrical, almost sacred central framing", tags="sublime"),
    F("a debris-field foreground framing the structure beyond", tags="desolate"),
    F("a first-person view from inside a slowly tumbling spacesuit", tags="melancholy"),
]

# Ordered so narrative axes resolve first; art axes then read the mood context.
AXES: dict[str, list[Fragment]] = {
    "structure": STRUCTURES,
    "technology": TECHNOLOGIES,
    "theme": THEMES,
    "lighting": LIGHTING,
    "palette": PALETTE,
    "composition": COMPOSITION,
}


# --------------------------------------------------------------------------- #
# Generator
# --------------------------------------------------------------------------- #

class NoCoherentConceptError(RuntimeError):
    """Raised when no valid concept satisfies the active constraints."""


@dataclass
class ConceptGenerator:
    """Assembles coherent concepts from the idea pools via backtracking."""

    axes: dict[str, list[Fragment]] = field(default_factory=lambda: AXES)
    require: frozenset[str] = frozenset()   # tags the final concept must include
    avoid: frozenset[str] = frozenset()     # tags the final concept must exclude

    def _pool(self, name: str) -> list[Fragment]:
        """Pool for an axis with `avoid`-tagged fragments pruned out."""
        pool = [f for f in self.axes[name] if not (f.tags & self.avoid)]
        if not pool:
            raise NoCoherentConceptError(
                f"Every option on axis '{name}' was excluded by --avoid."
            )
        return pool

    @staticmethod
    def _weighted_order(
        pool: list[Fragment], rng: random.Random, context_tags: frozenset[str]
    ) -> list[Fragment]:
        """Randomized order respecting weight and mood affinity.

        Uses the Efraimidis-Spirakis key (u ** (1/w)) so a single pass yields a
        correct weighted shuffle. Weight is boosted when a fragment shares a
        mood with the tags already committed to the concept.
        """
        ctx_moods = context_tags & MOODS
        keyed: list[tuple[float, Fragment]] = []
        for frag in pool:
            weight = frag.weight * (1.0 + MOOD_AFFINITY * len(frag.tags & ctx_moods))
            key = rng.random() ** (1.0 / max(weight, 1e-9))
            keyed.append((key, frag))
        keyed.sort(key=lambda pair: pair[0], reverse=True)
        return [frag for _, frag in keyed]

    @staticmethod
    def _compatible(
        frag: Fragment, acc_tags: frozenset[str], chosen: dict[str, Fragment]
    ) -> bool:
        """True if adding `frag` violates no conflict in either direction."""
        if frag.conflicts & (acc_tags | frag.tags):
            return False
        return not any(f.conflicts & frag.tags for f in chosen.values())

    def generate(self, rng: random.Random) -> dict[str, Fragment]:
        """Return one fragment per axis satisfying all constraints."""
        axis_names = list(self.axes)
        chosen: dict[str, Fragment] = {}

        def backtrack(i: int, acc_tags: frozenset[str]) -> bool:
            if i == len(axis_names):
                # All axes filled: verify cross-fragment `requires` and the
                # user's global --require filter against the full tag set.
                if not self.require <= acc_tags:
                    return False
                return all(f.requires <= acc_tags for f in chosen.values())

            name = axis_names[i]
            for frag in self._weighted_order(self._pool(name), rng, acc_tags):
                if not self._compatible(frag, acc_tags, chosen):
                    continue
                chosen[name] = frag
                if backtrack(i + 1, acc_tags | frag.tags):
                    return True
                del chosen[name]
            return False

        if not backtrack(0, frozenset()):
            raise NoCoherentConceptError(
                "No coherent concept satisfies the given constraints. "
                "Loosen --require / --avoid / --mood, or run --list-tags."
            )
        return dict(chosen)


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def prompt_sentence(concept: dict[str, Fragment]) -> str:
    """The original one-line format, preserved for backward compatibility."""
    return (
        f"A 3D scene depicting: {concept['structure'].text}, "
        f"{concept['technology'].text}, {concept['theme'].text}."
    )


def render(
    concept: dict[str, Fragment],
    seed: int,
    index: int,
    total: int,
    plain: bool = False,
) -> str:
    """Format a concept as either a plain logline or a full brief."""
    if plain:
        return prompt_sentence(concept)

    all_tags = sorted(frozenset().union(*(f.tags for f in concept.values())))
    lines = [
        "=" * 62,
        f"CONCEPT {index}/{total}".ljust(48) + f"seed {seed}",
        "=" * 62,
        "",
        "[ PROJECT PROMPT ]",
        textwrap.fill(prompt_sentence(concept), width=62, subsequent_indent="  "),
        "",
        "[ ART DIRECTION ]",
        f"  Lighting     : {concept['lighting'].text}",
        f"  Palette      : {concept['palette'].text}",
        f"  Composition  : {concept['composition'].text}",
        "",
        "[ TAGS ] " + ", ".join(all_tags),
    ]
    return "\n".join(lines)


def list_tags() -> str:
    """Human-readable inventory of every tag the pools can produce."""
    counts: dict[str, int] = {}
    for pool in AXES.values():
        for frag in pool:
            for tag in frag.tags:
                counts[tag] = counts.get(tag, 0) + 1
    width = max(len(t) for t in counts)
    body = "\n".join(
        f"  {tag.ljust(width)}  x{counts[tag]}{'  (mood)' if tag in MOODS else ''}"
        for tag in sorted(counts)
    )
    return "Available tags (usable with --require / --avoid):\n" + body


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate coherent hard-sci-fi concepts for 3D art.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 creative_code_quest.py\n"
            "  python3 creative_code_quest.py -n 3\n"
            "  python3 creative_code_quest.py --mood menacing --avoid organic\n"
            "  python3 creative_code_quest.py --require derelict --seed 1234 -n 1\n"
        ),
    )
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="number of concepts to generate (default: 1)")
    parser.add_argument("-s", "--seed", type=int, default=None,
                        help="master seed for reproducible output")
    parser.add_argument("--require", action="append", default=[], metavar="TAG",
                        help="require a tag (repeatable)")
    parser.add_argument("--avoid", action="append", default=[], metavar="TAG",
                        help="exclude a tag (repeatable)")
    parser.add_argument("--mood", action="append", default=[], choices=sorted(MOODS),
                        help="steer toward a mood (repeatable); implies --require")
    parser.add_argument("--plain", action="store_true",
                        help="emit only the one-line prompt (legacy format)")
    parser.add_argument("--list-tags", action="store_true",
                        help="print every available tag and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_tags:
        print(list_tags())
        return 0

    if args.count < 1:
        print("error: --count must be at least 1")
        return 2

    generator = ConceptGenerator(
        require=frozenset(args.require) | frozenset(args.mood),
        avoid=frozenset(args.avoid),
    )

    master_seed = args.seed if args.seed is not None else random.randrange(2**31)
    master = random.Random(master_seed)

    if not args.plain:
        print("--- Hard Sci-Fi Conceptual Seed Generator ---")

    outputs: list[str] = []
    for i in range(1, args.count + 1):
        # Each concept gets its own directly-reproducible seed. Reproduce any
        # single concept with:  --seed <printed seed> --count 1  (+ same filters)
        if args.count == 1 and args.seed is not None:
            sub_seed = args.seed
        else:
            sub_seed = master.randrange(2**31)

        try:
            concept = generator.generate(random.Random(sub_seed))
        except NoCoherentConceptError as err:
            print(f"error: {err}")
            return 1

        outputs.append(render(concept, sub_seed, i, args.count, plain=args.plain))

    print(("\n" if args.plain else "\n\n").join(outputs))
    return 0


# Backward-compatible entry point: prints a single full concept.
def generate_and_display_concept() -> None:
    main(["--count", "1"])


if __name__ == "__main__":
    raise SystemExit(main())
