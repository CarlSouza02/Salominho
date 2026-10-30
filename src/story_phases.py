"""Carregamento das fases por capítulo de Gênesis."""
from __future__ import annotations

import json
from pathlib import Path


GENESIS_PHASE_ANCHORS = {
    1: "genesis_001",
}


def _validate_phase(phase: dict) -> None:
    required = {
        "id",
        "order",
        "chapter",
        "title",
        "bible_reference",
        "objective",
        "characters",
        "key_events",
        "narration",
        "quiz",
        "devotional",
        "reward",
    }
    missing = sorted(required.difference(phase))
    if missing:
        raise ValueError(f"Fase sem campos obrigatórios: {', '.join(missing)}")

    if not isinstance(phase["chapter"], int) or phase["chapter"] < 1:
        raise ValueError(f'Capítulo inválido na fase {phase["id"]}')

    if not phase["narration"]:
        raise ValueError(f'Fase {phase["id"]} sem narração')

    if not phase["quiz"]:
        raise ValueError(f'Fase {phase["id"]} sem quiz')

    for question in phase["quiz"]:
        options = question.get("options", [])
        correct = question.get("correct_index")
        if not options or not isinstance(correct, int) or not (0 <= correct < len(options)):
            raise ValueError(f'Questão inválida na fase {phase["id"]}')


def load_genesis_story_phases(base: Path) -> dict[str, dict]:
    root = (
        Path(base)
        / "assets"
        / "worlds"
        / "old_testament"
        / "01_genesis"
        / "phases"
    )
    index = json.loads((root / "index.json").read_text(encoding="utf-8"))

    phases: dict[str, dict] = {}
    for entry in index.get("phases", []):
        payload = json.loads(
            (root / entry["file"]).read_text(encoding="utf-8")
        )
        _validate_phase(payload)
        if entry.get("chapter") != payload["chapter"]:
            raise ValueError(f'Índice inconsistente para a fase {payload["id"]}')
        phases[payload["id"]] = payload

    return phases
