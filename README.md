# Hard Sci-Fi Idea Generator

A small CLI that breaks creative block for 3D artists working on narrative, hard-sci-fi portfolio pieces.

It assembles a grammatical project prompt from megastructures, speculative technology, and a societal or philosophical theme, then adds art-direction notes for lighting, camera, surface, and scale.

## Requirements

Python 3.10 or newer. No third-party packages.

## Usage

```bash
python creative_code_quest.py
```

```
============================================================
 HARD SCI-FI CONCEPT  ·  seed 184291
============================================================

[ PROJECT PROMPT ]
A 3D scene depicting a derelict Ringworld segment being
deconstructed by self-replicating Von Neumann probes, built
as a monument to a civilization's greatest failure.

[ ART DIRECTION ]
Lighting    : hard rim light from a dying binary sun, deep umber shadows
Camera      : wide anamorphic establishing shot, low horizon, massive scale
Surface     : pitted nickel-iron hull plated with frost and micrometeor scoring
Scale cue   : a maintenance drone the size of a city
```

### Options

| Flag | Meaning |
| --- | --- |
| `-n`, `--count N` | Generate N concepts |
| `-s`, `--seed N` | Reproduce a previous concept. A batch uses `seed`, `seed+1`, … |
| `-b`, `--brief` | Print only the one-line prompt |
| `-j`, `--json` | Print JSON (includes the assembled prompt) |
| `-o`, `--output PATH` | Write to a file instead of stdout |

```bash
python creative_code_quest.py --count 5 --brief
python creative_code_quest.py --seed 42
python creative_code_quest.py --json --output concepts.json
```

## Tests

```bash
python -m unittest discover -v
```
