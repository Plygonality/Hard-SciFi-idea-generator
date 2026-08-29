#!/usr/bin/env python3
"""Tests for the hard sci-fi concept generator."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path

import creative_code_quest as quest


class CatalogTests(unittest.TestCase):
    def test_catalogs_are_nonempty(self) -> None:
        for name in (
            "STRUCTURES",
            "CONDITIONS",
            "THEMES",
            "LIGHTING",
            "CAMERAS",
            "SURFACES",
            "SCALE_CUES",
        ):
            catalog = getattr(quest, name)
            self.assertGreater(len(catalog), 0, msg=name)
            self.assertEqual(len(catalog), len(set(catalog)), msg=f"duplicates in {name}")

    def test_fragments_have_no_trailing_punctuation(self) -> None:
        for catalog in (
            quest.STRUCTURES,
            quest.CONDITIONS,
            quest.THEMES,
            quest.LIGHTING,
            quest.CAMERAS,
            quest.SURFACES,
            quest.SCALE_CUES,
        ):
            for fragment in catalog:
                self.assertFalse(fragment.endswith("."), msg=fragment)
                self.assertEqual(fragment, fragment.strip(), msg=fragment)


class GenerationTests(unittest.TestCase):
    def test_same_seed_is_reproducible(self) -> None:
        first = quest.generate_concept(seed=42)
        second = quest.generate_concept(seed=42)
        self.assertEqual(first, second)

    def test_different_seeds_diverge(self) -> None:
        first = quest.generate_concept(seed=1)
        second = quest.generate_concept(seed=2)
        self.assertNotEqual(first, second)

    def test_prompt_assembles_slots(self) -> None:
        concept = quest.generate_concept(seed=7)
        self.assertIn(concept.structure, concept.prompt)
        self.assertIn(concept.condition, concept.prompt)
        self.assertIn(concept.theme, concept.prompt)
        self.assertTrue(concept.prompt.startswith("A 3D scene depicting "))
        self.assertTrue(concept.prompt.endswith("."))

    def test_batch_uses_offset_seeds(self) -> None:
        batch = quest.generate_concepts(count=3, seed=100)
        self.assertEqual([item.seed for item in batch], [100, 101, 102])
        self.assertEqual(batch[0], quest.generate_concept(seed=100))
        self.assertEqual(batch[2], quest.generate_concept(seed=102))

    def test_invalid_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            quest.generate_concepts(count=0)


class FormatTests(unittest.TestCase):
    def test_full_format_includes_art_direction(self) -> None:
        concept = quest.generate_concept(seed=9)
        text = quest.format_concept(concept)
        self.assertIn(f"seed {concept.seed}", text)
        self.assertIn(concept.prompt, text)
        self.assertIn(concept.lighting, text)
        self.assertIn(concept.camera, text)
        self.assertIn(concept.surface, text)
        self.assertIn(concept.scale_cue, text)

    def test_brief_format_is_one_labeled_line(self) -> None:
        concept = quest.generate_concept(seed=9)
        text = quest.format_concept(concept, brief=True)
        self.assertEqual(text.count("\n"), 1)
        self.assertIn(concept.prompt, text)
        self.assertNotIn("ART DIRECTION", text)

    def test_json_format_is_valid_and_includes_prompt(self) -> None:
        concepts = quest.generate_concepts(count=2, seed=3)
        payload = json.loads(quest.format_concepts(concepts, as_json=True))
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["seed"], 3)
        self.assertEqual(payload[0]["prompt"], concepts[0].prompt)
        self.assertEqual(payload[0]["structure"], concepts[0].structure)


class CliTests(unittest.TestCase):
    def test_cli_seed_matches_library(self) -> None:
        buffer = StringIO()
        status = quest.main(["--seed", "42", "--brief"], stream=buffer)
        self.assertEqual(status, 0)
        expected = quest.format_concept(quest.generate_concept(seed=42), brief=True)
        self.assertEqual(buffer.getvalue(), expected)

    def test_cli_rejects_bad_count(self) -> None:
        status = quest.main(["--count", "0"], stream=StringIO())
        self.assertEqual(status, 2)

    def test_cli_writes_output_file(self) -> None:
        concept = quest.generate_concept(seed=11)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "concept.txt"
            status = quest.main(
                ["--seed", "11", "--brief", "--output", str(path)],
                stream=StringIO(),
            )
            self.assertEqual(status, 0)
            self.assertEqual(path.read_text(encoding="utf-8"), quest.format_concept(concept, brief=True))


if __name__ == "__main__":
    unittest.main()
