"""Persistência local do progresso do jogador."""
from __future__ import annotations

import json
from pathlib import Path


class Progress:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = {"xp": 0, "chapters": {}, "phases": {}}
        self.load()

    def load(self) -> None:
        if not self.path.is_file():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self.data["xp"] = int(payload.get("xp", 0))
                self.data["chapters"] = dict(payload.get("chapters", {}))
                self.data["phases"] = dict(payload.get("phases", {}))
        except (OSError, ValueError, TypeError):
            pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def key(world_id: str, chapter: int) -> str:
        return f"{world_id}:{chapter}"

    @property
    def xp(self) -> int:
        return int(self.data.get("xp", 0))

    def chapter(self, world_id: str, chapter: int) -> dict:
        key = self.key(world_id, chapter)
        return dict(self.data["chapters"].get(key, {
            "read": False,
            "mastered": False,
            "best_score": 0,
        }))

    def mark_read(self, world_id: str, chapter: int, xp_reward: int = 20) -> bool:
        key = self.key(world_id, chapter)
        state = self.chapter(world_id, chapter)
        first_time = not state["read"]
        state["read"] = True
        self.data["chapters"][key] = state
        if first_time:
            self.data["xp"] += xp_reward
        self.save()
        return first_time

    def record_quiz(
        self,
        world_id: str,
        chapter: int,
        score: int,
        total: int,
        xp_per_correct: int = 10,
        mastery_bonus: int = 20,
    ) -> dict:
        key = self.key(world_id, chapter)
        state = self.chapter(world_id, chapter)
        previous_best = int(state.get("best_score", 0))
        score = max(0, min(int(score), int(total)))

        if score > previous_best:
            self.data["xp"] += (score - previous_best) * xp_per_correct
            state["best_score"] = score

        mastered_now = total > 0 and score == total
        first_mastery = mastered_now and not state.get("mastered", False)
        if first_mastery:
            state["mastered"] = True
            self.data["xp"] += mastery_bonus

        self.data["chapters"][key] = state
        self.save()
        return {
            "first_mastery": first_mastery,
            "mastered": bool(state.get("mastered", False)),
            "best_score": int(state.get("best_score", 0)),
            "xp": self.xp,
        }

    def phase(self, phase_id: str) -> dict:
        return dict(self.data["phases"].get(phase_id, {
            "completed": False,
            "mastered": False,
            "best_score": 0,
        }))

    def record_story_phase(
        self,
        phase_id: str,
        score: int,
        total: int,
        completion_bonus: int = 20,
        xp_per_correct: int = 10,
        mastery_bonus: int = 20,
    ) -> dict:
        state = self.phase(phase_id)
        score = max(0, min(int(score), int(total)))
        previous_best = int(state.get("best_score", 0))

        first_completion = not bool(state.get("completed", False))
        if first_completion:
            state["completed"] = True
            self.data["xp"] += completion_bonus

        if score > previous_best:
            self.data["xp"] += (score - previous_best) * xp_per_correct
            state["best_score"] = score

        mastered_now = total > 0 and score == total
        first_mastery = mastered_now and not bool(state.get("mastered", False))
        if first_mastery:
            state["mastered"] = True
            self.data["xp"] += mastery_bonus

        self.data["phases"][phase_id] = state
        self.save()

        return {
            "first_completion": first_completion,
            "first_mastery": first_mastery,
            "completed": bool(state.get("completed", False)),
            "mastered": bool(state.get("mastered", False)),
            "best_score": int(state.get("best_score", 0)),
            "xp": self.xp,
        }

    def count_world(self, world_id: str, chapters: int) -> tuple[int, int]:
        read = mastered = 0
        for chapter in range(1, chapters + 1):
            state = self.chapter(world_id, chapter)
            read += int(bool(state.get("read")))
            mastered += int(bool(state.get("mastered")))
        return read, mastered
