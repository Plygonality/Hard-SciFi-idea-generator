#!/usr/bin/env python3
"""Tests for the coherence-aware hard sci-fi concept generator."""

from __future__ import annotations

import random
import unittest
from io import StringIO
from unittest.mock import patch

import creative_code_quest as quest


def concept_tags(concept: dict[str, quest.Fragment]) -> frozenset[str]:
    return frozenset().union(*(frag.tags for frag in concept.values()))


def generate(
    seed: int = 0,
    require: frozenset[str] | set[str] = frozenset(),
    avoid: frozenset[str] | set[str] = frozenset(),
) -> dict[str, quest.Fragment]:
    return quest.ConceptGenerator(
        require=frozenset(require),
        avoid=frozenset(avoid),
    ).generate(random.Random(seed))


class CatalogTests(unittest.TestCase):
    POOLS = (
        "STRUCTURES",
        "TECHNOLOGIES",
        "THEMES",
        "LIGHTING",
        "PALETTE",
        "COMPOSITION",
    )

    def test_catalogs_are_nonempty_and_unique(self) -> None:
        for name in self.POOLS:
            catalog = getattr(quest, name)
            self.assertGreater(len(catalog), 0, msg=name)
            texts = [frag.text for frag in catalog]
            self.assertEqual(len(texts), len(set(texts)), msg=f"duplicates in {name}")

    def test_axes_cover_every_pool(self) -> None:
        self.assertEqual(set(quest.AXES), {
            "structure",
            "technology",
            "theme",
            "lighting",
            "palette",
            "composition",
        })

    def test_fragments_are_trimmed_and_unpunctuated(self) -> None:
        for name in self.POOLS:
            for frag in getattr(quest, name):
                self.assertEqual(frag.text, frag.text.strip(), msg=frag.text)
                self.assertFalse(frag.text.endswith("."), msg=frag.text)

    def test_moods_are_labeled(self) -> None:
        self.assertTrue(quest.MOODS <= {
            "desolate", "sublime", "menacing", "melancholy", "uncanny",
        })


class CoherenceTests(unittest.TestCase):
    def assert_coherent(self, concept: dict[str, quest.Fragment]) -> None:
        tags = concept_tags(concept)
        for frag in concept.values():
            self.assertTrue(
                frag.requires <= tags,
                msg=f"{frag.text!r} missing required {frag.requires - tags}",
            )
            self.assertFalse(
                frag.conflicts & tags,
                msg=f"{frag.text!r} conflicts with {frag.conflicts & tags}",
            )
            for other in concept.values():
                self.assertFalse(
                    other.conflicts & frag.tags,
                    msg=f"{other.text!r} forbids tags from {frag.text!r}",
                )

    def test_default_generation_is_always_coherent(self) -> None:
        for seed in range(80):
            self.assert_coherent(generate(seed=seed))

    def test_abandoned_ruin_is_never_under_construction(self) -> None:
        constructing = "being constructed by self-replicating Von Neumann probes"
        for seed in range(80):
            concept = generate(seed=seed)
            tags = concept_tags(concept)
            if {"abandoned", "derelict"} & tags:
                self.assertNotEqual(concept["technology"].text, constructing)

    def test_uninhabited_sites_have_no_living_archives(self) -> None:
        living = "where the last organic beings are kept as living archives"
        for seed in range(80):
            concept = generate(seed=seed)
            if "uninhabited" in concept_tags(concept):
                self.assertNotEqual(concept["theme"].text, living)

    def test_require_is_honored(self) -> None:
        for seed in range(20):
            concept = generate(seed=seed, require={"derelict"})
            self.assertIn("derelict", concept_tags(concept))
            self.assert_coherent(concept)

    def test_avoid_is_honored(self) -> None:
        for seed in range(20):
            concept = generate(seed=seed, avoid={"organic"})
            self.assertNotIn("organic", concept_tags(concept))
            self.assert_coherent(concept)

    def test_impossible_constraints_raise(self) -> None:
        with self.assertRaises(quest.NoCoherentConceptError):
            generate(require={"constructing", "deconstructing"})

    def test_avoiding_every_mood_empties_art_direction(self) -> None:
        with self.assertRaises(quest.NoCoherentConceptError):
            generate(avoid=quest.MOODS)


class GenerationTests(unittest.TestCase):
    def test_same_seed_is_reproducible(self) -> None:
        first = generate(seed=42)
        second = generate(seed=42)
        self.assertEqual(
            {key: frag.text for key, frag in first.items()},
            {key: frag.text for key, frag in second.items()},
        )

    def test_different_seeds_can_diverge(self) -> None:
        texts = {
            tuple(frag.text for frag in generate(seed=seed).values())
            for seed in range(12)
        }
        self.assertGreater(len(texts), 1)

    def test_prompt_assembles_narrative_slots(self) -> None:
        concept = generate(seed=7)
        sentence = quest.prompt_sentence(concept)
        self.assertIn(concept["structure"].text, sentence)
        self.assertIn(concept["technology"].text, sentence)
        self.assertIn(concept["theme"].text, sentence)
        self.assertTrue(sentence.startswith("A 3D scene depicting: "))
        self.assertTrue(sentence.endswith("."))

    def test_full_render_includes_art_direction_and_tags(self) -> None:
        concept = generate(seed=9)
        text = quest.render(concept, seed=9, index=1, total=1)
        self.assertIn("seed 9", text)
        self.assertIn(quest.prompt_sentence(concept), text)
        self.assertIn(concept["lighting"].text, text)
        self.assertIn(concept["palette"].text, text)
        self.assertIn(concept["composition"].text, text)
        self.assertIn("[ TAGS ]", text)

    def test_plain_render_is_the_logline(self) -> None:
        concept = generate(seed=9)
        self.assertEqual(
            quest.render(concept, seed=9, index=1, total=1, plain=True),
            quest.prompt_sentence(concept),
        )


class CliTests(unittest.TestCase):
    def test_cli_seed_matches_library(self) -> None:
        expected = quest.prompt_sentence(generate(seed=42))
        with patch("sys.stdout", new=StringIO()) as out:
            status = quest.main(["--seed", "42", "--plain"])
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue().strip(), expected)

    def test_cli_rejects_bad_count(self) -> None:
        with patch("sys.stdout", new=StringIO()) as out:
            status = quest.main(["--count", "0"])
        self.assertEqual(status, 2)
        self.assertIn("error:", out.getvalue())

    def test_cli_require_and_mood(self) -> None:
        with patch("sys.stdout", new=StringIO()) as out:
            status = quest.main([
                "--seed", "11",
                "--require", "derelict",
                "--mood", "menacing",
            ])
        self.assertEqual(status, 0)
        text = out.getvalue()
        self.assertIn("derelict", text)
        self.assertIn("menacing", text)
        self.assertIn("[ ART DIRECTION ]", text)

    def test_cli_impossible_filters(self) -> None:
        with patch("sys.stdout", new=StringIO()) as out:
            status = quest.main([
                "--require", "constructing",
                "--require", "deconstructing",
            ])
        self.assertEqual(status, 1)
        self.assertIn("error:", out.getvalue())

    def test_list_tags(self) -> None:
        with patch("sys.stdout", new=StringIO()) as out:
            status = quest.main(["--list-tags"])
        self.assertEqual(status, 0)
        text = out.getvalue()
        self.assertIn("derelict", text)
        self.assertIn("(mood)", text)


if __name__ == "__main__":
    unittest.main()
