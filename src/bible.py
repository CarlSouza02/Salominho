"""Leitura bíblica por capítulo via API, cache e fallback local."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

import requests

CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"

BOOK_DISPLAY_NAMES = {
    "genesis": "Gênesis",
}

FALLBACK_GENESIS_1 = {
    "reference": "Gênesis 1",
    "translation": "Bíblia Livre (amostra offline)",
    "verses": [
        {"number": 1, "text": "No princípio criou Deus os céus e a terra."}
    ],
    "attribution": (
        "Bíblia Livre (2018), Diego Santos, Mario Sérgio e Marco Teles, "
        "https://ebible.org/porbr2018/, CC BY 4.0 Brasil."
    ),
    "offline": True,
}


def normalize_api_response(
    payload: dict,
    fallback_reference: str = "Passagem bíblica",
) -> dict:
    verses = payload.get("verses") or []
    cleaned = [
        {
            "number": int(v["verse"]),
            "text": re.sub(r"\s+", " ", v["text"]).strip(),
        }
        for v in verses
        if "verse" in v and isinstance(v.get("text"), str)
    ]
    if not cleaned:
        raise ValueError("API retornou uma passagem sem versículos válidos")
    return {
        "reference": payload.get("reference", fallback_reference),
        "translation": "João Ferreira de Almeida (bible-api.com)",
        "verses": cleaned,
        "attribution": "Texto fornecido por bible-api.com, tradução almeida.",
        "offline": False,
    }


def _offline_fallback(book: str, chapter: int) -> dict:
    if book == "genesis" and chapter == 1:
        return dict(FALLBACK_GENESIS_1)

    display = BOOK_DISPLAY_NAMES.get(book, book.replace("_", " ").title())
    return {
        "reference": f"{display} {chapter}",
        "translation": "Leitura indisponível offline",
        "verses": [],
        "attribution": "",
        "offline": True,
    }


def get_bible_chapter(
    book: str,
    chapter: int,
    timeout: float = 4.0,
) -> dict:
    book = str(book).strip().lower()
    chapter = int(chapter)
    if chapter < 1:
        raise ValueError("O capítulo deve ser positivo")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{book}_{chapter}_almeida.json"
    display = BOOK_DISPLAY_NAMES.get(book, book.replace("_", " ").title())
    reference = f"{display} {chapter}"
    query = f"{book} {chapter}"
    url = "https://bible-api.com/" + quote(query, safe=":-")

    try:
        response = requests.get(
            url,
            params={"translation": "almeida"},
            timeout=timeout,
            headers={"User-Agent": "Salominho/0.4.4 (educational prototype)"},
        )
        response.raise_for_status()
        passage = normalize_api_response(
            response.json(),
            fallback_reference=reference,
        )
        cache_path.write_text(
            json.dumps(passage, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return passage
    except (
        requests.RequestException,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ):
        if cache_path.is_file():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                if isinstance(cached.get("verses"), list) and cached["verses"]:
                    cached["offline"] = True
                    return cached
            except (OSError, ValueError, TypeError, KeyError):
                pass
        return _offline_fallback(book, chapter)


def get_creation_passage(timeout: float = 4.0) -> dict:
    """Compatibilidade com o protótipo e testes antigos."""
    return get_bible_chapter("genesis", 1, timeout=timeout)
