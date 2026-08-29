#!/usr/bin/env python3
"""Hard Sci-Fi Concept Generator for 3D Artists.

Generates a unique, high-concept prompt for a 3D art project focused on
megastructural engineering, speculative technology, and the societal or
philosophical implications they raise.

Designed to break a creative block and support narrative-driven portfolio work.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import textwrap
from dataclasses import asdict, dataclass
from typing import Sequence, TextIO

# ---------------------------------------------------------------------------
# Catalogs
# Each slot is written so fragments can be assembled into a grammatical
# English sentence:
#   "A 3D scene depicting {structure} {condition}, {theme}."
# Art-direction fields are labeled extras for lighting, camera, and surface.
# ---------------------------------------------------------------------------

STRUCTURES: tuple[str, ...] = (
    "a derelict Ringworld segment",
    "a partially completed Dyson swarm",
    "the computational core of a Matrioshka brain",
    "a generation ship arriving at a dead world",
    "a space elevator tethered to a rogue planet",
    "an automated Von Neumann factory on an interstellar asteroid",
    "an Alderson disk abandoned mid-terraforming",
    "a Shkadov thruster being assembled around a neutron star",
    "a stellar-mass black hole mined for energy via the Penrose process",
    "the interior of a Jupiter brain",
    "a Stanford torus frozen in a failed spin-up",
    "a magnetic orbital ring around a tidally locked world",
    "a stellar engine nudging a dying sun off its galactic course",
    "a hollowed nickel-iron asteroid converted into a city-ship",
    "a Bishop ring grazing the upper atmosphere of a gas giant",
)

CONDITIONS: tuple[str, ...] = (
    "powered by a contained micro-singularity",
    "being deconstructed by self-replicating Von Neumann probes",
    "being constructed by self-replicating Von Neumann probes",
    "housing the uploaded minds of its long-dormant builders",
    "fractured by a local spacetime anomaly",
    "acting as a cradle for an autonomous artificial intelligence",
    "fabricated from exotic matter with negative mass",
    "having achieved sentience and now resisting its organic creators",
    "opening a stable traversable wormhole with exotic-matter scaffolding",
    "drifting through a nebula of dark-matter filaments",
    "radiating waste heat as a structured infrared beacon",
    "held together by active support that is continuously failing",
    "harvesting Hawking radiation from an evaporating micro black hole",
    "running on a computronium substrate that is beginning to sublime",
    "locked in a centuries-long bootstrap sequence that never completed",
)

THEMES: tuple[str, ...] = (
    "where the last organic beings are kept as living archives",
    "built as a monument to a civilization's greatest failure",
    "in a society that has outlawed individual consciousness",
    "abandoned after its inhabitants transcended physical form",
    "whose sole purpose is to observe the final moments of the universe",
    "serving as a safe harbor from a vacuum-decay front",
    "whose inhabitants are de-evolving after losing the knowledge to maintain it",
    "now contested territory between biological and synthetic life",
    "where reality is a programmable simulation beginning to decay",
    "dedicated to preserving one unaltered second of a dead Earth",
    "whose crew still debates whether they are the original travelers or copies",
    "used to hide a civilization from a predatory interstellar intelligence",
    "where time dilation has split one people into two irreconcilable histories",
    "whose ethics engine will not allow the structure to be powered down",
    "waiting for a signal that was never going to arrive",
)

LIGHTING: tuple[str, ...] = (
    "hard rim light from a dying binary sun, deep umber shadows",
    "volumetric god-rays cutting through frozen outgassing",
    "cold blue reactor glow against a red-giant sky",
    "eclipse lighting: a thin photosphere crescent and dense starfield",
    "sodium-orange maintenance floods on kilometer-scale interiors",
    "Cherenkov-blue light bleeding from a containment failure",
    "starlight only, with surfaces reading as near-silhouette",
    "caustic light from a nearby accretion disk",
    "overcast light from a Dyson swarm's incomplete shell",
    "strobing warning beacons in a power-dead megastructure",
)

CAMERAS: tuple[str, ...] = (
    "wide anamorphic establishing shot, low horizon, massive scale",
    "three-point architectural interior with a human figure for scale",
    "top-down orthographic slice revealing layered systems",
    "tracking shot along a tether that disappears into cloud",
    "Dutch-angle wreckage study with extreme foreground debris",
    "macro-to-vista: a glove or tool in frame, the structure beyond",
    "cross-section cutaway, as if the model were a technical illustration",
    "aerial approach toward a silhouette that keeps revealing more scale",
    "locked-off hero shot suitable for a portfolio thumbnail",
    "over-the-shoulder from a maintenance drone's viewport",
)

SURFACES: tuple[str, ...] = (
    "pitted nickel-iron hull plated with frost and micrometeor scoring",
    "carbon-nanotube weave with failed active-support ribs",
    "ceramic heat-shield tiles peeling from a stellar-engine nozzle",
    "computronium that reads as dark, densely etched metal",
    "aerogel insulation torn open to expose glowing coolant lines",
    "basalt regolith sintered into structural foam",
    "self-healing polymer skin bubbling at vacuum tears",
    "gold-anodized radiator fins the size of continents",
    "ice-and-rock composite with embedded superconducting mesh",
    "tarnished beryllium mirrors from a stellar-light collector",
)

SCALE_CUES: tuple[str, ...] = (
    "a maintenance drone the size of a city",
    "a single human figure standing on a rib that spans the horizon",
    "a fleet of habitat cylinders no larger than rivets on the structure",
    "an entire weather system trapped inside a broken bay",
    "a river of molten slag falling for tens of kilometers",
    "windows that resolve into city grids only at extreme close range",
    "a tether so long it disappears before the curvature is visible",
    "construction printers laying a beam wider than a mountain range",
)


@dataclass(frozen=True)
class Concept:
    """A complete hard-sci-fi seed for a 3D scene."""

    seed: int
    structure: str
    condition: str
    theme: str
    lighting: str
    camera: str
    surface: str
    scale_cue: str

    @property
    def prompt(self) -> str:
        """One grammatical sentence an artist can drop into a brief."""
        return f"A 3D scene depicting {self.structure} {self.condition}, {self.theme}."


def _pick(rng: random.Random, options: Sequence[str]) -> str:
    return rng.choice(options)


def generate_concept(seed: int | None = None) -> Concept:
    """Build one concept. A given seed always returns the same concept."""
    if seed is None:
        seed = random.SystemRandom().randint(0, 2**32 - 1)
    rng = random.Random(seed)
    return Concept(
        seed=seed,
        structure=_pick(rng, STRUCTURES),
        condition=_pick(rng, CONDITIONS),
        theme=_pick(rng, THEMES),
        lighting=_pick(rng, LIGHTING),
        camera=_pick(rng, CAMERAS),
        surface=_pick(rng, SURFACES),
        scale_cue=_pick(rng, SCALE_CUES),
    )


def generate_concepts(count: int = 1, seed: int | None = None) -> list[Concept]:
    """Generate ``count`` concepts.

    If ``seed`` is provided, the first concept uses that seed and each
    following concept uses ``seed + index`` so a batch is reproducible.
    """
    if count < 1:
        raise ValueError("count must be at least 1")
    concepts: list[Concept] = []
    for index in range(count):
        item_seed = None if seed is None else seed + index
        concepts.append(generate_concept(item_seed))
    return concepts


def format_concept(concept: Concept, *, brief: bool = False) -> str:
    """Render a concept as a readable art brief."""
    if brief:
        return f"[seed {concept.seed}] {concept.prompt}\n"

    body = textwrap.dedent(
        f"""\
        ============================================================
         HARD SCI-FI CONCEPT  ·  seed {concept.seed}
        ============================================================

        [ PROJECT PROMPT ]
        {concept.prompt}

        [ ART DIRECTION ]
        Lighting    : {concept.lighting}
        Camera      : {concept.camera}
        Surface     : {concept.surface}
        Scale cue   : {concept.scale_cue}

        ------------------------------------------------------------
        """
    )
    return body


def format_concepts(
    concepts: Sequence[Concept],
    *,
    brief: bool = False,
    as_json: bool = False,
) -> str:
    """Render one or more concepts as text or JSON."""
    if as_json:
        payload = [
            {**asdict(concept), "prompt": concept.prompt} for concept in concepts
        ]
        return json.dumps(payload, indent=2) + "\n"

    return "\n".join(format_concept(concept, brief=brief) for concept in concepts)


def generate_and_display_concept() -> None:
    """Original entry point: print a single fully formatted concept."""
    sys.stdout.write(format_concept(generate_concept()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="creative_code_quest",
        description=(
            "Generate hard-sci-fi concept seeds for narrative 3D portfolio work."
        ),
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="number of concepts to generate (default: 1)",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="reproducible seed; batch items use seed, seed+1, ...",
    )
    parser.add_argument(
        "-b",
        "--brief",
        action="store_true",
        help="print only the one-line prompt",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        dest="as_json",
        help="print concepts as JSON",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="write to PATH instead of stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None, stream: TextIO | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        concepts = generate_concepts(count=args.count, seed=args.seed)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    text = format_concepts(concepts, brief=args.brief, as_json=args.as_json)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        (stream or sys.stdout).write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
