import tempfile
import unittest
from pathlib import Path

from src.progress import Progress
from src.story_phases import GENESIS_PHASE_ANCHORS, load_genesis_story_phases


class StoryPhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(__file__).resolve().parents[1]
        cls.phases = load_genesis_story_phases(cls.base)

    def test_first_two_genesis_chapters_are_playable(self):
        self.assertEqual(len(self.phases), 2)
        self.assertEqual(
            set(self.phases),
            {"genesis_001", "genesis_002"},
        )
        self.assertEqual(
            GENESIS_PHASE_ANCHORS,
            {1: "genesis_001", 2: "genesis_002"},
        )

        phase1 = self.phases["genesis_001"]
        self.assertEqual(phase1["chapter"], 1)
        self.assertEqual(phase1["expected_verses"], 31)
        self.assertEqual(len(phase1["narration"]), 6)
        self.assertEqual(len(phase1["quiz"]), 5)

        phase2 = self.phases["genesis_002"]
        self.assertEqual(phase2["chapter"], 2)
        self.assertEqual(phase2["expected_verses"], 25)
        self.assertEqual(len(phase2["narration"]), 6)
        self.assertEqual(len(phase2["quiz"]), 5)

    def test_quiz_answers_are_valid(self):
        for phase in self.phases.values():
            for question in phase["quiz"]:
                self.assertTrue(question["options"])
                self.assertTrue(
                    0 <= question["correct_index"] < len(question["options"])
                )

    def test_phase_progress_is_separate_from_reading_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Progress(Path(tmp) / "progress.json")
            result = progress.record_story_phase("genesis_002", 5, 5)

            self.assertTrue(result["completed"])
            self.assertTrue(result["mastered"])
            self.assertFalse(progress.chapter("genesis", 2)["read"])
            self.assertEqual(progress.phase("genesis_002")["best_score"], 5)


if __name__ == "__main__":
    unittest.main()
