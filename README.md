# Hard Sci-Fi Idea Generator

Hard sci-fi concept generator for 3D artists. Builds coherent megastructure prompts with lighting, palette, and composition notes.

Use it to break a creative block and seed narrative-driven portfolio work: megastructural engineering, speculative technology, and the societal or philosophical questions those structures raise. Each run is a production brief, not just a logline — a grammatical project prompt plus art-direction notes for lighting, palette, and composition, biased toward the mood of the story.

Fragments carry semantic tags and optional `requires` / `conflicts` rules. A backtracking solver keeps combinations coherent, so an abandoned ruin will not appear under active construction, and de-evolving inhabitants will not turn up in a structure with no one left. Seeds are reproducible; `--require`, `--avoid`, and `--mood` let you steer.

## Requirements

Python 3.10 or newer. No third-party packages.

## Usage

```bash
python3 Hard-SciFi_Idea_Generator.py
```

```
==============================================================
CONCEPT 1/1                                     seed 1234
==============================================================

[ PROJECT PROMPT ]
A 3D scene depicting: a derelict Ringworld segment,
  being deconstructed by self-replicating Von Neumann
  probes, built as a monument to a civilization's
  greatest failure.

[ ART DIRECTION ]
  Lighting     : harsh, unfiltered starlight raking across bare metal
  Palette      : oxidized copper, rust, and deep shadow
  Composition  : a debris-field foreground framing the structure beyond

[ TAGS ] abandoned, deconstructing, derelict, desolate, melancholy, ...
```

### Options

| Flag | Meaning |
| --- | --- |
| `-n`, `--count N` | Generate N concepts |
| `-s`, `--seed N` | Reproduce a previous concept (the printed seed is enough) |
| `--require TAG` | Keep only concepts that include this tag (repeatable) |
| `--avoid TAG` | Exclude this tag (repeatable) |
| `--mood MOOD` | Steer toward `desolate`, `sublime`, `menacing`, `melancholy`, or `uncanny` |
| `--plain` | Print only the one-line prompt |
| `--list-tags` | Show every tag the pools can produce |

```bash
python3 Hard-SciFi_Idea_Generator.py -n 3
python3 Hard-SciFi_Idea_Generator.py --mood menacing --avoid organic
python3 Hard-SciFi_Idea_Generator.py --require derelict --seed 1234
python3 Hard-SciFi_Idea_Generator.py --list-tags
```

Reproduce any printed concept with the same filters and `--seed <printed seed> --count 1`.

## Tests

```bash
python3 -m unittest discover -v
```
