"""Leitura demonstrativa da Bíblia via API, cache e fallback licenciado."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

import requests

CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"
FALLBACK = {
    "reference": "Gênesis 1:1",
    "translation": "Bíblia Livre (amostra offline)",
    "verses": [{"number": 1, "text": "No princípio criou Deus os céus e a terra."}],
    "attribution": (
        "Bíblia Livre (2018), Diego Santos, Mario Sérgio e Marco Teles, "
        "https://ebible.org/porbr2018/, CC BY 4.0 Brasil."
    ),
    "offline": True,
}


def normalize_api_response(payload: dict) -> dict:
    verses = payload.get("verses") or []
    cleaned = [
        {"number": int(v["verse"]), "text": re.sub(r"\s+", " ", v["text"]).strip()}
        for v in verses
        if "verse" in v and isinstance(v.get("text"), str)
    ]
    if not cleaned:
        raise ValueError("API retornou uma passagem sem versículos válidos")
    return {
        "reference": payload.get("reference", "Gênesis 1:1-5"),
        "translation": "João Ferreira de Almeida (bible-api.com)",
        "verses": cleaned,
        "attribution": "Texto fornecido por bible-api.com, tradução almeida.",
        "offline": False,
    }


def get_creation_passage(timeout: float = 4.0) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / "genesis_1_1-5_almeida.json"
    url = "https://bible-api.com/" + quote("genesis 1:1-5", safe=":-")
    try:
        response = requests.get(
            url,
            params={"translation": "almeida"},
            timeout=timeout,
            headers={"User-Agent": "Salominho/0.1 (educational prototype)"},
        )
        response.raise_for_status()
        passage = normalize_api_response(response.json())
        cache_path.write_text(json.dumps(passage, ensure_ascii=False, indent=2), encoding="utf-8")
        return passage
    except (requests.RequestException, OSError, ValueError, KeyError, TypeError):
        if cache_path.is_file():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                if isinstance(cached.get("verses"), list) and cached["verses"]:
                    cached["offline"] = True
                    return cached
            except (OSError, ValueError, TypeError, KeyError):
                pass
        return dict(FALLBACK)
